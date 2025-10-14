# Core configuration and settings
from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    """Application settings and configuration"""
    
    # API Configuration
    app_name: str = "RepoLens API"
    app_version: str = "2.0.0"
    debug: Optional[str] = None
    
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
        ".py", ".js", ".ts", ".jsx", ".tsx", 
        ".java", ".cpp", ".c", ".cs", ".go", 
        ".rs", ".php", ".rb", ".swift", ".kt"
    ]
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    
    # CORS
    cors_origins: list = [
        "http://localhost:3000",
        "http://localhost:3001",
        "https://repolens.org",
        "https://www.repolens.org",
        "https://app.repolens.org"
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = False
        extra = "ignore"  # Ignore extra fields

# Global settings instance
settings = Settings()