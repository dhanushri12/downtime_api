"""
═══════════════════════════════════════════════════════════════════════
CONFIGURATION MODULE
═══════════════════════════════════════════════════════════════════════
Centralized configuration management for all environment variables.
Uses pydantic for validation and type safety.
"""

from pydantic_settings import BaseSettings
from typing import List
import logging

# ═══════════════════════════════════════════════
# CONFIGURATION CLASS
# ═══════════════════════════════════════════════


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    
    Attributes:
        All database, email, API, and server configuration properties.
    """

    # ─────────────────────────────────────────────
    # DATABASE CONFIGURATION
    # ─────────────────────────────────────────────
    DATABASE_URL: str = "postgresql://postgres:vRefex123@localhost:5432/downtimedb"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "downtimedb"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "vRefex123"

    # ─────────────────────────────────────────────
    # EMAIL CONFIGURATION
    # ─────────────────────────────────────────────
    EMAIL_ADDRESS: str = "dhanushrihh@gmail.com"
    EMAIL_PASSWORD: str = "Dhanu@2005"
    EMAIL_HOST: str = "smtp.gmail.com"
    EMAIL_PORT: int = 587

    # ─────────────────────────────────────────────
    # APPLICATION CONFIGURATION
    # ─────────────────────────────────────────────
    APP_NAME: str = "Wind Turbine SCADA Dashboard"
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    SECRET_KEY: str = "vdi gxgg lnrm jdvq"

    # ─────────────────────────────────────────────
    # API CONFIGURATION
    # ─────────────────────────────────────────────
    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:5173,http://localhost:4173"

    # ─────────────────────────────────────────────
    # SERVER CONFIGURATION
    # ─────────────────────────────────────────────
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8000

    # ─────────────────────────────────────────────
    # LOGGING CONFIGURATION
    # ─────────────────────────────────────────────
    LOG_LEVEL: str = "INFO"

    # ─────────────────────────────────────────────
    # FILE UPLOAD CONFIGURATION
    # ─────────────────────────────────────────────
    MAX_UPLOAD_SIZE: int = 5242880  # 5MB
    UPLOAD_DIR: str = "uploads/profile_photos"

    # ─────────────────────────────────────────────
    # OTP CONFIGURATION
    # ─────────────────────────────────────────────
    OTP_EXPIRY_MINUTES: int = 10

    # ─────────────────────────────────────────────
    # EXTERNAL API ENDPOINTS
    # ─────────────────────────────────────────────
    IP_GEOLOCATION_API: str = "http://ip-api.com/json"
    PUBLIC_IP_API: str = "https://api64.ipify.org?format=json"
    WEATHER_API: str = "https://api.open-meteo.com/v1/forecast"

    class Config:
        """Pydantic config for reading from .env file."""
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

    def get_cors_origins(self) -> List[str]:
        """
        Parse CORS origins from comma-separated string.
        
        Returns:
            List of CORS origins.
        """
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    def is_production(self) -> bool:
        """
        Check if application is running in production.
        
        Returns:
            True if environment is production, False otherwise.
        """
        return self.APP_ENV.lower() == "production"

    def is_development(self) -> bool:
        """
        Check if application is running in development.
        
        Returns:
            True if environment is development, False otherwise.
        """
        return self.APP_ENV.lower() == "development"


# ═══════════════════════════════════════════════
# GLOBAL SETTINGS INSTANCE
# ═══════════════════════════════════════════════

settings = Settings()

