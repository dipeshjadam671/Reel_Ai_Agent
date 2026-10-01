from typing import List, Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
import os

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    # Application
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    LOG_LEVEL: str = "INFO"
    APP_NAME: str = "Autonomous Video AI Platform"
    API_V1_PREFIX: str = "/api/v1"
    SECRET_KEY: str = "dev-secret-key-change-in-production-min-32-chars-long"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 43200  # 30 days
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://127.0.0.1:3000"]

    # Budget & Retries
    DEFAULT_WORKSPACE_BUDGET_USD: float = 50.00
    MAX_CYCLE_RETRIES: int = 3
    APPROVAL_TIMEOUT_HOURS: int = 72

    # Database & Cache
    DATABASE_URL: str = "sqlite+aiosqlite:///./test.db"
    DATABASE_SYNC_URL: str = "sqlite:///./test.db"
    REDIS_URL: str = "redis://localhost:6379/0"

    # Storage
    STORAGE_BACKEND: str = "local"  # "local" or "s3"
    LOCAL_STORAGE_PATH: str = "/tmp/video_ai_platform/storage"
    S3_BUCKET_NAME: str = "video-ai-platform-assets"
    S3_REGION: str = "us-east-1"
    S3_ACCESS_KEY_ID: Optional[str] = None
    S3_SECRET_ACCESS_KEY: Optional[str] = None
    S3_ENDPOINT_URL: Optional[str] = None

    # Mock Mode Switch
    MOCK_EXTERNAL_APIS: bool = True

    # LLM Configuration
    DEFAULT_LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: Optional[str] = None
    ANTHROPIC_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None
    LLM_CHEAP_MODEL: str = "gpt-4o-mini"
    LLM_REASONING_MODEL: str = "gpt-4o"
    LLM_FALLBACK_MODEL: str = "gemini-1.5-flash"

    # Search Configuration
    SEARCH_PROVIDER: str = "duckduckgo"
    TAVILY_API_KEY: Optional[str] = None
    SERPAPI_API_KEY: Optional[str] = None

    # Media & Stock
    PEXELS_API_KEY: Optional[str] = None
    UNSPLASH_ACCESS_KEY: Optional[str] = None

    # TTS
    TTS_PROVIDER: str = "elevenlabs"
    ELEVENLABS_API_KEY: Optional[str] = None
    ELEVENLABS_DEFAULT_VOICE_ID: str = "21m00Tcm4TlvDq8ikWAM"

    # Avatar
    AVATAR_PROVIDER: str = "heygen"
    HEYGEN_API_KEY: Optional[str] = None
    DID_API_KEY: Optional[str] = None

    # Social Publishing
    YOUTUBE_CLIENT_ID: Optional[str] = None
    YOUTUBE_CLIENT_SECRET: Optional[str] = None
    YOUTUBE_REDIRECT_URI: str = "http://localhost:8000/api/v1/social-accounts/callback/youtube"

    INSTAGRAM_APP_ID: Optional[str] = None
    INSTAGRAM_APP_SECRET: Optional[str] = None
    INSTAGRAM_REDIRECT_URI: str = "http://localhost:8000/api/v1/social-accounts/callback/instagram"

    TIKTOK_CLIENT_KEY: Optional[str] = None
    TIKTOK_CLIENT_SECRET: Optional[str] = None
    TIKTOK_REDIRECT_URI: str = "http://localhost:8000/api/v1/social-accounts/callback/tiktok"

    # Webhooks
    WEBHOOK_SECRET: str = "dev-webhook-signature-secret"

settings = Settings()
