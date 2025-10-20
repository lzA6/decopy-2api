from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List, Optional, Dict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding='utf-8',
        extra="ignore"
    )

    APP_NAME: str = "decopy-2api"
    APP_VERSION: str = "1.0.0"
    DESCRIPTION: str = "一个将 decopy.ai 转换为兼容 OpenAI 格式 API 的高性能代理。"

    API_MASTER_KEY: Optional[str] = None
    
    # Decopy.ai 静态凭证
    PRODUCT_CODE: Optional[str] = "067003"
    PRODUCT_SERIAL: Optional[str] = "eb0f5222701cbd6e67799c0cb99ec32b"

    API_REQUEST_TIMEOUT: int = 180
    NGINX_PORT: int = 8088

    # 模型名称映射
    MODEL_MAPPING: Dict[str, str] = {
        "decopy-deepseek-v3": "DeepSeek-V3",
        "decopy-gemini-2.0-flash": "Gemini-2.0-Flash",
        "decopy-gpt-4o-mini": "GPT-4o-mini",
        "decopy-deepseek-r1": "DeepSeek-R1"
    }
    DEFAULT_MODEL: str = "decopy-deepseek-v3"

settings = Settings()
