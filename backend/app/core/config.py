# Core configuration and settings
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings and configuration"""

    # API Configuration
    app_name: str = "RepoLens API"
    app_version: str = "2.0.0"
    debug: str = "false"

    # Database Configuration
    database_url: str = "postgresql+asyncpg://postgres:password@localhost:5432/repolens"

    # Redis Configuration
    redis_url: str = "redis://localhost:6379"

    # OpenAI Configuration
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    openai_max_tokens: int = 4000
    openai_temperature: float = 0.1

    # AI Analysis Configuration
    ai_analysis_enabled: bool = True
    ai_max_tokens: int = 4000
    ai_temperature: float = 0.1

    # Logging
    log_level: str = "INFO"

    # Repository Analysis
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    supported_extensions: list = [
        ".py",
        ".js",
        ".ts",
        ".jsx",
        ".tsx",
        ".java",
        ".cpp",
        ".c",
        ".cs",
        ".go",
        ".rs",
        ".php",
        ".rb",
        ".swift",
        ".kt",
    ]

    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60

    # Authentication Configuration
    jwt_secret_key: str = "your-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7

    # OAuth Configuration
    google_client_id: Optional[str] = None
    google_client_secret: Optional[str] = None
    github_client_id: Optional[str] = None
    github_client_secret: Optional[str] = None

    # Frontend URL for OAuth redirects
    frontend_url: str = "http://localhost:3000"

    # CORS
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://repolens.org",
        "https://www.repolens.org",
        "https://app.repolens.org",
    ]

    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields


# Global settings instance
settings = Settings()
