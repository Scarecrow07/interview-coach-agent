from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """配置管理"""
    
    # DeepSeek 配置
    DEEPSEEK_API_KEY: str
    DEEPSEEK_MODEL: Literal["deepseek-chat", "deepseek-coder"] = "deepseek-chat"
    DEEPSEEK_BASE_URL: str = "https://api.deepseek.com/v1"
    
    # 缓存配置
    REDIS_URL: str = "redis://localhost:6379"
    CACHE_TTL_HOURS: int = 24
    
    # 会话配置
    SESSION_TTL_HOURS: int = 24
    
    # 日志配置
    LOG_LEVEL: Literal["DEBUG", "INFO", "WARNING", "ERROR"] = "INFO"
    
    # Prompt 版本
    PROMPT_VERSION: str = "v1.0"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()