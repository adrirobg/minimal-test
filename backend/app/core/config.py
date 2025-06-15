"""
Application settings and configuration using Pydantic Settings
"""
from typing import List
from pydantic_settings import BaseSettings
from pydantic import field_validator
import os
from pathlib import Path


class Settings(BaseSettings):
    """Application settings with Pydantic validation."""
    
    # Database
    database_url: str = "postgresql+asyncpg://kairos:kairos@localhost:5432/kairos"
    
    # Security
    secret_key: str = "kairos-dev-secret"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000"]
    
    # Environment
    environment: str = "development"
    debug: bool = True
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    
    # API
    api_v1_prefix: str = "/api/v1"
    project_name: str = "Kairos BCP"
    version: str = "1.0.0"
    description: str = "Personal Knowledge Management System"
    
    @field_validator("allowed_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()