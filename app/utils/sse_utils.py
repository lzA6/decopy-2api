import json
import time
from typing import Dict, Any, Optional

def create_sse_data(data: Dict[str, Any]) -> str:
    """将字典数据格式化为 SSE 事件字符串。"""
    return f"data: {json.dumps(data, ensure_ascii=False)}\n\n"

def create_chat_completion_chunk(
    request_id: str,
    model: str,
    content: str,
    finish_reason: Optional[str] = None
) -> Dict[str, Any]:
    """创建一个与 OpenAI 兼容的聊天补全流式块。"""
    return {
        "id": request_id,
        "object": "chat.completion.chunk",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "delta": {"content": content},
                "finish_reason": finish_reason
            }
        ]
    }

# --- [新增] 创建与 OpenAI 兼容的非流式聊天补全响应 ---
def create_chat_completion_response(
    request_id: str,
    model: str,
    content: str,
    finish_reason: str
) -> Dict[str, Any]:
    """创建一个与 OpenAI 兼容的完整、非流式聊天补全响应。"""
    return {
        "id": request_id,
        "object": "chat.completion",
        "created": int(time.time()),
        "model": model,
        "choices": [
            {
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": content
                },
                "finish_reason": finish_reason
            }
        ],
        "usage": {
            "prompt_tokens": 0, # 注意：目前无法从上游获取准确的 token 数
            "completion_tokens": 0,
            "total_tokens": 0
        }
    }

DONE_CHUNK = create_sse_data({"id": "done", "object": "done", "choices": [], "created": int(time.time()), "model": "done"})
