"""
Configuration management - loads from .env file
"""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings"""
    
    # App
    APP_NAME: str = "Traffic Share"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    
    # Security
    SECRET_KEY: str = Field(..., min_length=32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    
    # Database
    DATABASE_URL: str = Field(..., description="PostgreSQL connection string")
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_ECHO: bool = False
    
    # Redis
    REDIS_URL: str = Field(..., description="Redis connection string")
    REDIS_KEY_PREFIX: str = "traffic_share:"
    
    # Telegram Bot
    TELEGRAM_BOT_TOKEN: str = Field(..., description="Telegram bot token")
    TELEGRAM_ADMIN_IDS: str = Field(..., description="Comma-separated admin Telegram IDs")
    TELEGRAM_ADMIN_CHANNEL: Optional[str] = None
    
    # Cryptomus Payment Gateway
    CRYPTOMUS_API_KEY: str = Field(..., description="Cryptomus API key")
    CRYPTOMUS_MERCHANT_ID: str = Field(..., description="Cryptomus merchant ID")
    CRYPTOMUS_API_URL: str = "https://api.cryptomus.com/v1"
    CRYPTOMUS_WEBHOOK_SECRET: Optional[str] = None
    
    # IP & Region Check
    IP_API_ENABLED: bool = True
    REGION_CHECK_ENABLED: bool = True
    
    # Traffic & Pricing
    PRICE_PER_GB: float = 0.50
    MIN_WITHDRAWAL_AMOUNT: float = 5.0
    MAX_WITHDRAWAL_AMOUNT: float = 1000.0
    
    # Package Allocation
    PACKAGE_ALLOCATION_TTL: int = 60  # seconds
    MAX_PACKAGES_PER_REQUEST: int = 10
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_AUTH: str = "10/minute"
    RATE_LIMIT_TRAFFIC_UPDATE: str = "100/minute"
    RATE_LIMIT_BUYER_PULL: str = "10/minute"
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/traffic_share.log"
    LOG_MAX_SIZE_MB: int = 10
    LOG_BACKUP_COUNT: int = 5
    
    # CORS
    CORS_ORIGINS: str = "*"
    
    # Background Tasks
    CLEANUP_TASK_INTERVAL: int = 300  # 5 minutes
    STATS_TASK_INTERVAL: int = 3600  # 1 hour
    BACKUP_TASK_INTERVAL: int = 86400  # 24 hours
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def get_admin_ids(self) -> list[int]:
        """Parse admin IDs from comma-separated string"""
        try:
            return [int(id.strip()) for id in self.TELEGRAM_ADMIN_IDS.split(",")]
        except Exception:
            return []
    
    def get_cors_origins(self) -> list[str]:
        """Parse CORS origins"""
        if self.CORS_ORIGINS == "*":
            return ["*"]
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]


# Global settings instance
settings = Settings()
