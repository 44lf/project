from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    PROJECT_NAME: str = "K12智能教育平台"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "基于OCR和LLM的K12智能作业批改平台"
    
    # 数据库配置
    DATABASE_URL: str = "sqlite:///./k12_education.db"
    
    # 安全配置
    SECRET_KEY: str = "your-secret-key-here-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 文件上传配置
    UPLOAD_DIR: str = "uploads"
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # 10MB
    ALLOWED_EXTENSIONS: set = {"png", "jpg", "jpeg", "gif", "bmp"}
    
    # OCR配置
    OCR_CONFIDENCE_THRESHOLD: float = 0.85  # 置信度阈值
    OCR_LANG: str = "chi_sim+eng"  # Tesseract语言包
    
    # 人工审核配置
    MANUAL_REVIEW_THRESHOLD: float = 0.70  # 低于此置信度转人工审核
    
    # Redis配置（Celery消息队列）
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # LLM配置（兼容国内模型如Qwen、DeepSeek）
    LLM_BASE_URL: str = "https://api.openai.com/v1"  # 兼容国内模型
    LLM_API_KEY: str = "your-api-key"
    LLM_MODEL_NAME: str = "qwen-plus"  # 或 deepseek-chat
    
    class Config:
        env_file = ".env"


settings = Settings()
