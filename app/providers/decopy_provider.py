import time
import json
import uuid
import asyncio
import base64
from typing import Dict, Any, AsyncGenerator, List

import cloudscraper
import httpx
from fastapi import HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from loguru import logger

from app.core.config import settings
from app.providers.base_provider import BaseProvider
from app.utils.sse_utils import create_sse_data, create_chat_completion_chunk, DONE_CHUNK

class DecopyProvider(BaseProvider):
    def __init__(self):
        self.scraper = cloudscraper.create_scraper()
        self.create_job_url = "https://api.decopy.ai/api/decopy/ask-ai/create-job"
        self.get_job_url_template = "https://api.decopy.ai/api/decopy/ask-ai/get-job/{job_id}"

    async def chat_completion(self, request_data: Dict[str, Any]) -> StreamingResponse:
        
        async def stream_generator() -> AsyncGenerator[bytes, None]:
            request_id = f"chatcmpl-{uuid.uuid4()}"
            model_name = request_data.get("model", settings.DEFAULT_MODEL)
            
            try:
                headers = self._prepare_headers()
                files, chat_id = await self._prepare_form_data(request_data)
                
                logger.info(f"向 Decopy 提交任务, 模型: {model_name}, Chat ID: {chat_id}")

                logger.debug(f"--- [REQUEST TO DECOPY (CREATE JOB)] ---\nURL: POST {self.create_job_url}\nHeaders: {headers}\nPayload (multipart): Omitted for brevity\n-----------------------------------------")

                loop = asyncio.get_running_loop()
                response = await loop.run_in_executor(
                    None, 
                    lambda: self.scraper.post(self.create_job_url, headers=headers, files=files)
                )
                
                response_json = response.json()
                logger.debug(f"--- [RESPONSE FROM DECOPY (CREATE JOB)] ---\nStatus: {response.status_code}\nBody: {json.dumps(response_json, indent=2, ensure_ascii=False)}\n-------------------------------------------")

                response.raise_for_status()
                
                if response_json.get("code") != 100000:
                    raise HTTPException(status_code=502, detail=f"上游创建任务失败: {response_json.get('message', {}).get('zh', '未知错误')}")
                
                job_id = response_json.get("result", {}).get("job_id")
                if not job_id:
                    raise HTTPException(status_code=502, detail="上游响应中未找到 job_id。")
                
                logger.info(f"任务提交成功, Job ID: {job_id}. 开始获取 SSE 流...")

                stream_url = self.get_job_url_template.format(job_id=job_id)
                
                logger.debug(f"--- [REQUEST TO DECOPY (GET STREAM)] ---\nURL: GET {stream_url}\nHeaders: {headers}\n----------------------------------------")
                
                stream_response = await loop.run_in_executor(
                    None,
                    lambda: self.scraper.get(stream_url, headers=headers, stream=True)
                )
                
                logger.info(f"获取 SSE 流响应状态码: {stream_response.status_code}")
                stream_response.raise_for_status()

                # 【最终修正】正确处理增量JSON流
                for line in stream_response.iter_lines():
                    logger.trace(f"Raw SSE line: {line}")
                    if line.startswith(b"data:"):
                        content_str = line[len(b"data:"):].strip().decode('utf-8', errors='ignore')
                        
                        if content_str == 'Data transfer completed.':
                            logger.info("检测到 'Data transfer completed.' 消息，流结束。")
                            continue
                        
                        if not content_str:
                            continue
                            
                        try:
                            # 解析每一行独立的 JSON 对象
                            data = json.loads(content_str)
                            # 提取 'data' 字段作为增量内容
                            delta_content = data.get("data")
                            
                            if delta_content is not None:
                                # 直接将增量内容封装并发送
                                chunk = create_chat_completion_chunk(request_id, model_name, delta_content)
                                yield create_sse_data(chunk)
                        except json.JSONDecodeError:
                            logger.warning(f"无法解析 SSE 数据块: {content_str}")
                            continue
                
                logger.info(f"Job ID: {job_id} 的流处理完毕。")
                final_chunk = create_chat_completion_chunk(request_id, model_name, "", "stop")
                yield create_sse_data(final_chunk)
                yield DONE_CHUNK

            except Exception as e:
                logger.error(f"处理流时发生错误: {e}", exc_info=True)
                error_message = f"内部服务器错误: {str(e)}"
                error_chunk = create_chat_completion_chunk(request_id, model_name, error_message, "stop")
                yield create_sse_data(error_chunk)
                yield DONE_CHUNK

        return StreamingResponse(stream_generator(), media_type="text/event-stream")

    def _prepare_headers(self) -> Dict[str, str]:
        return {
            "Accept": "*/*",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Origin": "https://decopy.ai",
            "Referer": "https://decopy.ai/",
            "product-code": settings.PRODUCT_CODE,
            "product-serial": settings.PRODUCT_SERIAL,
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/141.0.0.0 Safari/537.36",
        }

    async def _prepare_form_data(self, request_data: Dict[str, Any]) -> tuple[Dict[str, Any], str]:
        messages = request_data.get("messages", [])
        if not messages:
            raise HTTPException(status_code=400, detail="请求中缺少 'messages' 字段。")

        last_user_message = next((m for m in reversed(messages) if m.get("role") == "user"), None)
        if not last_user_message or not last_user_message.get("content"):
            raise HTTPException(status_code=400, detail="未找到有效的用户消息。")

        prompt_text = ""
        image_url = None
        
        content = last_user_message["content"]
        if isinstance(content, str):
            prompt_text = content
        elif isinstance(content, list):
            for part in content:
                if part.get("type") == "text":
                    prompt_text = part.get("text", "")
                elif part.get("type") == "image_url":
                    image_url = part.get("image_url", {}).get("url")

        model_name = request_data.get("model", settings.DEFAULT_MODEL)
        actual_model = settings.MODEL_MAPPING.get(model_name, "DeepSeek-V3")
        
        chat_id = str(uuid.uuid4())
        
        files = {
            "entertext": (None, prompt_text),
            "chat_id": (None, chat_id),
            "model": (None, actual_model),
            "chat_group": (None, ""),
        }

        if image_url:
            logger.info(f"检测到图片 URL，正在下载: {image_url[:100]}...")
            async with httpx.AsyncClient() as client:
                if image_url.startswith("data:image/"):
                    header, encoded = image_url.split(",", 1)
                    image_bytes = base64.b64decode(encoded)
                    file_extension = header.split("/")[1].split(";")[0]
                else:
                    response = await client.get(image_url)
                    response.raise_for_status()
                    image_bytes = response.content
                    file_extension = image_url.split('.')[-1].split('?')[0] or 'jpg'

            files["upload_images"] = (f"image.{file_extension}", image_bytes, f"image/{file_extension}")
            logger.info(f"图片已准备好上传，大小: {len(image_bytes)} bytes")

        return files, chat_id

    async def get_models(self) -> JSONResponse:
        model_data = {
            "object": "list",
            "data": [
                {"id": name, "object": "model", "created": int(time.time()), "owned_by": "lzA6"}
                for name in settings.MODEL_MAPPING.keys()
            ]
        }
        return JSONResponse(content=model_data)
