"""
Configuration module for Autonomous Agent Pro.
Manages all environment variables and application settings.
"""

from pydantic_settings import BaseSettings
from typing import Optional
from enum import Enum


class LLMProvider(str, Enum):
    """Supported LLM providers."""
    DEEPSEEK = "deepseek"
    OPENAI = "openai"
    CLAUDE = "claude"
    LLAMA = "llama"
    GROQ = "groq"


class ExecutionMode(str, Enum):
    """Code execution modes."""
    SAFE = "safe"  # Requires user approval
    AUTO = "auto"  # Automatic execution
    SANDBOX = "sandbox"  # Isolated execution


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "Autonomous Agent Pro"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    RELOAD: bool = False
    WORKERS: int = 4
    
    # LLM Configuration
    DEFAULT_LLM_PROVIDER: LLMProvider = LLMProvider.DEEPSEEK
    LLM_MODEL: str = "deepseek-chat"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 4096
    LLM_TIMEOUT: int = 60
    
    # API Keys
    DEEPSEEK_API_KEY: Optional[str] = None
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    
    # Execution Settings
    EXECUTION_MODE: ExecutionMode = ExecutionMode.SAFE
    EXECUTION_TIMEOUT: int = 300  # 5 minutes
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 2
    SANDBOX_ENABLED: bool = True
    
    # Code Execution
    ALLOWED_LANGUAGES: list = ["python", "javascript", "shell", "bash", "java", "r", "ruby"]
    RESTRICTED_MODULES: list = ["os", "sys", "subprocess", "socket"]
    MAX_OUTPUT_LENGTH: int = 10000
    
    # Voice & Audio
    WHISPER_MODEL: str = "base"
    AUDIO_SAMPLE_RATE: int = 16000
    MAX_AUDIO_DURATION: int = 600  # 10 minutes
    
    # Database
    DATABASE_URL: str = "mysql+pymysql://user:password@localhost/agent_db"
    DATABASE_POOL_SIZE: int = 10
    DATABASE_MAX_OVERFLOW: int = 20
    
    # Redis Cache
    REDIS_URL: str = "redis://localhost:6379/0"
    CACHE_TTL: int = 3600
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS
    CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:5173"]
    CORS_CREDENTIALS: bool = True
    CORS_METHODS: list = ["*"]
    CORS_HEADERS: list = ["*"]
    
    # File Storage
    UPLOAD_DIR: str = "./uploads"
    MAX_UPLOAD_SIZE: int = 100 * 1024 * 1024  # 100MB
    
    # Vision & Screen Control
    ENABLE_VISION: bool = True
    ENABLE_SCREEN_CONTROL: bool = True
    SCREEN_CAPTURE_INTERVAL: int = 5
    
    # Logging
    LOG_FILE: str = "./logs/agent.log"
    LOG_MAX_BYTES: int = 10485760  # 10MB
    LOG_BACKUP_COUNT: int = 5
    
    # Monitoring & Telemetry
    ENABLE_TELEMETRY: bool = False
    SENTRY_DSN: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
