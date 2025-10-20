<div align="center">

# ✨ decopy-2api ✨

<img src="https://img.shields.io/badge/license-Apache_2.0-blue.svg" alt="License">
<img src="https://img.shields.io/badge/Python-3.10+-brightgreen.svg" alt="Python Version">
<img src="https://img.shields.io/badge/Docker-Ready-blue.svg" alt="Docker Ready">
<img src="https://img.shields.io/badge/FastAPI-0.104+-green.svg" alt="FastAPI">
<img src="https://img.shields.io/github/stars/lzA6/decopy-2api?style=social" alt="GitHub Stars">

**将 `decopy.ai` 免费服务转换为兼容 OpenAI 格式 API 的高性能代理**

**让免费的翅膀，也能在标准的天空中翱翔** 🚀

</div>

---

> **致所有探索者、创造者和梦想家：**
>
> 在数字世界中，我们常常寻找打开新大门的钥匙。`decopy-2api` 就是这样一把钥匙——它不创造魔法，但将已有的魔法重新编排，让你以最熟悉、最优雅的方式（OpenAI API 格式）来驾驭它。
>
> 这不仅是一个项目，更是一种思想的实践：**开放、连接、创造**。我们相信技术的价值在于降低门槛，让更多人参与创造。当你启动这个项目时，不仅是启动服务，更是点亮一盏灯，照亮通往 AI 应用的又一条小径。

## 📖 目录

1. [🌟 项目亮点](#-项目亮点)
2. [🔮 核心原理](#-核心原理)
3. [📂 项目结构](#-项目结构)
4. [🛠️ 技术架构](#️-技术架构)
5. [🚀 快速部署](#-快速部署)
6. [💻 API 使用](#-api-使用)
7. [⚖️ 场景分析](#️-场景分析)
8. [🔭 未来规划](#-未来规划)
9. [🤖 开发蓝图](#-开发蓝图)
10. [📜 开源协议](#-开源协议)

## 🌟 项目亮点

### 核心价值
- **💰 零成本体验**：通过 `decopy.ai` 免费使用多种大模型（DeepSeek-V3, Gemini-2.0-Flash, GPT-4o-mini）
- **🔌 生态兼容**：完全兼容 OpenAI `v1/chat/completions` 接口标准
- **🖼️ 多模态支持**：支持图片上传和视觉对话
- **💨 流式响应**：享受实时打字机般的交互体验
- **🐳 一键部署**：Docker-Compose 简化部署流程

### 技术特色
```python
# 标准 OpenAI 客户端直接使用
client = openai.OpenAI(
    api_key="your_key",
    base_url="http://your-server:8088/v1"
)
```

## 🔮 核心原理

### 架构概览

```mermaid
graph TB
    A[📱 用户应用] -->|OpenAI API 请求| B[🌐 Nginx 网关]
    B -->|反向代理| C[🚀 FastAPI 服务]
    C -->|调用| D[🔄 DecopyProvider]
    D -->|模拟浏览器| E[🛡️ Cloudscraper]
    E -->|HTTP 请求| F[🎯 decopy.ai API]
    F -->|AI 服务| G[🤖 大模型集群]
    
    G -->|流式响应| F
    F -->|SSE 数据| E
    E -->|数据解析| D
    D -->|格式转换| C
    C -->|OpenAI 格式| B
    B -->|最终响应| A
    
    style A fill:#e1f5fe
    style C fill:#f3e5f5
    style D fill:#e8f5e8
    style E fill:#fff3e0
    style F fill:#ffebee
    style G fill:#fce4ec
```

### 工作流程详解

#### 1. **请求接收** 📬
```python
# 用户发送标准 OpenAI 请求
{
    "model": "decopy-gpt-4o-mini",
    "messages": [{"role": "user", "content": "Hello!"}],
    "stream": True
}
```

#### 2. **请求转发** 🔄
- FastAPI 接收并验证请求
- 选择对应的 Provider (DecopyProvider)
- 准备请求头和表单数据

#### 3. **任务创建** 🎯
```python
# 向 decopy.ai 提交任务
response = cloudscraper.post(
    "https://api.decopy.ai/api/decopy/ask-ai/create-job",
    headers=headers,
    files=files,
    data=form_data
)
job_id = response.json()["job_id"]
```

#### 4. **流式获取** 💫
```python
# 轮询获取任务结果
stream_response = cloudscraper.get(
    f"https://api.decopy.ai/api/decopy/ask-ai/get-job/{job_id}",
    stream=True,
    headers=headers
)

# 实时转换数据格式
for line in stream_response.iter_lines():
    if line.startswith(b'data: '):
        data = json.loads(line[6:])
        chunk = create_chat_completion_chunk(data["choices"][0]["delta"])
        yield f"data: {json.dumps(chunk)}\n\n"
```

#### 5. **响应返回** ✅
```python
# 流式返回 OpenAI 格式数据
return StreamingResponse(
    stream_generator(),
    media_type="text/event-stream"
)
```

## 📂 项目结构

```
decopy-2api/
├── 🐳 Docker 部署文件
│   ├── Dockerfile              # 容器构建配置
│   └── docker-compose.yml      # 服务编排配置
├── 🔧 配置文件
│   ├── .env.example           # 环境变量模板
│   ├── .env                   # 实际环境配置
│   └── nginx.conf             # Nginx 反向代理配置
├── 🚀 核心代码
│   ├── main.py                # FastAPI 应用入口
│   ├── requirements.txt       # Python 依赖列表
│   └── app/                   # 应用核心模块
│       ├── core/
│       │   ├── __init__.py
│       │   └── config.py      # 配置管理
│       ├── providers/
│       │   ├── __init__.py
│       │   ├── base_provider.py    # 提供商基类
│       │   └── decopy_provider.py  # decopy.ai 实现
│       └── utils/
│           └── sse_utils.py   # 流式工具函数
└── 📚 文档
    └── README.md              # 项目说明文档
```

## 🛠️ 技术架构

### 技术栈深度解析

| 组件 | 版本 | 作用 | 选择理由 | 替代方案 |
|------|------|------|----------|----------|
| **Python** | 3.10+ | 核心编程语言 | 丰富的AI生态，异步支持 | Go, Node.js |
| **FastAPI** | 0.104+ | Web API 框架 | 高性能，自动文档，类型提示 | Flask, Django |
| **Uvicorn** | 0.24+ | ASGI 服务器 | FastAPI 官方推荐，高性能 | Hypercorn, Daphne |
| **Cloudscraper** | 1.2.60+ | 反爬虫绕过 | 专攻Cloudflare防护 | Playwright, Selenium |
| **Httpx** | 0.25+ | 异步HTTP客户端 | 支持异步，API友好 | aiohttp, requests |
| **Loguru** | 0.7+ | 日志记录 | 配置简单，输出美观 | 内置logging |
| **Docker** | 20.10+ | 容器化部署 | 环境一致性，易于部署 | Podman, 直接部署 |
| **Nginx** | 1.18+ | 反向代理 | 稳定，高性能 | Traefik, Caddy |

### 性能优化特性
```python
# 异步处理提升并发性能
@app.post("/v1/chat/completions")
async def chat_completions(request: ChatCompletionRequest):
    # 异步下载图片（如果存在）
    if request.messages[0].get("images"):
        await download_images_async(request.messages[0]["images"])
    
    # 使用线程池执行同步的cloudscraper请求
    return await run_in_executor(provider.chat_completion, request)
```

## 🚀 快速部署

### 环境准备
```bash
# 确保已安装 Docker 和 Docker Compose
docker --version
docker-compose --version
```

### 四步部署指南

#### 1. **克隆项目**
```bash
git clone https://github.com/lzA6/decopy-2api.git
cd decopy-2api
```

#### 2. **配置环境**
```bash
# 复制配置文件
cp .env.example .env

# 编辑配置（重要：修改API密钥！）
nano .env
```

**关键配置项：**
```ini
# .env 文件内容
API_MASTER_KEY=sk-your-super-secret-key-here-12345
NGINX_PORT=8088
LOG_LEVEL=INFO
```

#### 3. **启动服务**
```bash
# 一键启动所有服务
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 查看实时日志
docker-compose logs -f
```

#### 4. **验证部署**
```bash
# 测试API连通性
curl http://localhost:8088/v1/models \
  -H "Authorization: Bearer sk-your-super-secret-key-here-12345"

# 预期响应：
{
  "object": "list",
  "data": [
    {
      "id": "decopy-deepseek-v3",
      "object": "model", 
      "created": 1677609600,
      "owned_by": "lzA6"
    }
  ]
}
```

### 部署验证流程图

```mermaid
graph LR
    A[🚀 开始部署] --> B[① 克隆代码]
    B --> C[② 配置环境]
    C --> D[③ 启动服务]
    D --> E[④ 验证测试]
    E --> F[✅ 部署成功]
    E --> G[❌ 部署失败]
    G --> H[🔧 检查日志]
    H --> C
    
    style A fill:#4caf50,color:white
    style F fill:#4caf50,color:white
    style G fill:#f44336,color:white
```

## 💻 API 使用

### 基础配置
```python
import openai

# 配置客户端
client = openai.OpenAI(
    api_key="sk-your-super-secret-key-here-12345",
    base_url="http://your-server:8088/v1"  # 替换为你的服务器地址
)
```

### 文本对话示例
```python
# 非流式对话
response = client.chat.completions.create(
    model="decopy-gpt-4o-mini",
    messages=[
        {"role": "system", "content": "你是一个有帮助的助手"},
        {"role": "user", "content": "请解释什么是机器学习"}
    ],
    stream=False
)

print(response.choices[0].message.content)
```

### 流式对话示例
```python
# 流式对话（推荐用于实时应用）
stream = client.chat.completions.create(
    model="decopy-deepseek-v3",
    messages=[{"role": "user", "content": "写一个Python快速排序算法"}],
    stream=True,
    max_tokens=1000
)

for chunk in stream:
    if chunk.choices[0].delta.content is not None:
        print(chunk.choices[0].delta.content, end="", flush=True)
```

### 图片对话示例
```python
import base64

# 读取并编码图片
with open("image.jpg", "rb") as image_file:
    base64_image = base64.b64encode(image_file.read()).decode('utf-8')

response = client.chat.completions.create(
    model="decopy-gpt-4o-mini", 
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "请描述这张图片的内容"},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/jpeg;base64,{base64_image}"
                    }
                }
            ]
        }
    ]
)
```

### 可用模型列表
```bash
curl http://localhost:8088/v1/models \
  -H "Authorization: Bearer your-api-key"
```

## ⚖️ 场景分析

### 适用场景 ✅

| 场景 | 推荐度 | 说明 |
|------|--------|------|
| **个人学习** | ⭐⭐⭐⭐⭐ | 零成本学习AI API调用 |
| **原型开发** | ⭐⭐⭐⭐ | 快速验证AI应用想法 |
| **内部工具** | ⭐⭐⭐ | 非核心业务辅助工具 |
| **技术研究** | ⭐⭐⭐⭐ | 探索不同模型特性 |

### 不适用场景 ❌

| 场景 | 风险等级 | 原因 |
|------|----------|------|
| **商业产品** | 🔴 高风险 | 稳定性无法保证 |
| **高并发服务** | 🔴 高风险 | 性能瓶颈明显 |
| **关键业务** | 🔴 高风险 | 服务可能随时中断 |
| **数据敏感应用** | 🟡 中风险 | 隐私保护有限 |

### 风险评估矩阵

```mermaid
quadrantChart
    title 风险评估矩阵
    x-axis "低风险" --> "高风险"
    y-axis "不推荐" --> "推荐"
    "个人学习": [0.2, 0.9]
    "原型开发": [0.3, 0.7]
    "内部工具": [0.6, 0.5]
    "技术研究": [0.4, 0.8]
    "商业产品": [0.9, 0.1]
    "高并发服务": [0.95, 0.1]
    "关键业务": [0.85, 0.2]
```

## 🔭 未来规划

### 近期目标 🎯
1. **错误处理优化**
   - 精细化异常处理
   - 标准化错误响应格式
   - 自动重试机制

2. **功能增强**
   - Token 使用量估算
   - 支持更多 Provider
   - 配置热重载

### 中期规划 📅
```python
# 计划中的多Provider支持
providers = {
    "decopy": DecopyProvider,
    "freegpt": FreeGPTProvider, 
    "other": OtherFreeProvider
}

# 智能路由选择
def select_provider(model: str) -> BaseProvider:
    if model.startswith("decopy-"):
        return providers["decopy"]
    elif model.startswith("freegpt-"):
        return providers["freegpt"]
```

### 长期愿景 🌟
- **插件化架构**：可插拔的Provider系统
- **Web管理界面**：可视化配置和监控
- **多云部署**：支持多种部署平台

### 开发路线图

```mermaid
timeline
    title 项目开发路线图
    section 2024 Q1
        核心功能稳定
        : 基础代理服务
        : Docker 部署优化
    section 2024 Q2  
        功能增强
        : 多Provider支持
        : 错误处理优化
    section 2024 Q3
        体验提升
        : Web管理界面
        : 性能监控
    section 2024 Q4
        生态扩展
        : 插件系统
        : 社区贡献
```

## 🤖 开发蓝图

### 核心架构解析

```python
# 核心执行流程（伪代码）
async def chat_completion_flow(request):
    # 1. 请求验证
    validate_request(request)
    
    # 2. 选择Provider
    provider = get_provider(request.model)
    
    # 3. 准备请求数据
    form_data = provider.prepare_form_data(request)
    
    # 4. 创建任务
    job_id = await create_decopy_job(form_data)
    
    # 5. 流式获取结果
    async for chunk in stream_decopy_results(job_id):
        # 6. 格式转换
        openai_chunk = convert_to_openai_format(chunk)
        yield openai_chunk
    
    # 7. 结束标志
    yield "[DONE]"
```

### 扩展开发指南

#### 添加新的 Provider
1. **继承基类**：
```python
class NewProvider(BaseProvider):
    async def chat_completion(self, request: ChatCompletionRequest):
        # 实现具体的请求逻辑
        pass
```

2. **注册Provider**：
```python
PROVIDERS = {
    "new-provider": NewProvider,
    "decopy": DecopyProvider
}
```

#### 性能优化建议
- 使用 `httpx.AsyncClient` 替换同步请求
- 实现连接池复用
- 添加请求缓存机制

## 📜 开源协议

### Apache 2.0 许可证要点

| 权利 | 义务 | 限制 |
|------|------|------|
| ✅ 商业使用 | 📝 保留版权声明 | ❌ 无担保 |
| ✅ 修改分发 | 📝 声明修改内容 | ⚠️ 责任限制 |
| ✅ 专利使用 | 📝 包含许可证文本 |  |

### 合规使用建议
1. **个人使用**：完全自由，无需授权
2. **商业使用**：允许但需遵守许可证条款
3. **修改分发**：必须明确标注修改内容
4. **集成到产品**：需要包含许可证文本

### 贡献指南
我们欢迎社区贡献！请通过：
- GitHub Issues 报告问题
- Pull Requests 提交代码
- Discussions 参与讨论

---

<div align="center">

## 🎉 开始使用

**选择你的使用方式：**

```bash
# 方式一：Docker部署（推荐）
docker-compose up -d

# 方式二：源码运行
pip install -r requirements.txt
python main.py

# 方式三：直接调用API
curl -X POST http://localhost:8088/v1/chat/completions \
  -H "Authorization: Bearer your-key" \
  -H "Content-Type: application/json" \
  -d '{"model": "decopy-gpt-4o-mini", "messages": [{"role": "user", "content": "Hello!"}]}'
```

**遇到问题？**
- 📚 查看详细文档
- 🐛 提交 Issue
- 💬 加入讨论

**如果这个项目对你有帮助，请给我们一个 ⭐ Star！**

*让开源精神继续传递* ❤️

</div>
