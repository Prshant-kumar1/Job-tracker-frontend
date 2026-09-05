"""
Application configuration.

Loads settings from environment variables (with sane local-dev defaults)
using pydantic-settings so the rest of the app never touches os.environ
directly.
"""
import os
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import field_validator, ValidationError


class Settings(BaseSettings):
    # JWT
    SECRET_KEY: str = "CHANGE_ME_TO_A_RANDOM_SECRET_IN_PRODUCTION"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30  # Refresh tokens last 30 days
    
    # Database
    DATABASE_URL: str = "sqlite:///./job_tracker.db"
    
    # Environment
    ENVIRONMENT: str = "development"  # development, staging, production
    
    # Pagination
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100

    # AI / LLM
    GEMINI_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
    @field_validator('SECRET_KEY')
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """Ensure SECRET_KEY is changed in production environments."""
        # Check if we're in production
        env = os.getenv("ENVIRONMENT", "development")
        
        if env in ["production", "staging"]:
            if v == "CHANGE_ME_TO_A_RANDOM_SECRET_IN_PRODUCTION":
                raise ValueError(
                    "SECRET_KEY must be set to a secure random value in production. "
                    "Generate one with: python -c \"import secrets; print(secrets.token_hex(32))\""
                )
            if len(v) < 32:
                raise ValueError(
                    "SECRET_KEY must be at least 32 characters long for security."
                )
        elif v == "CHANGE_ME_TO_A_RANDOM_SECRET_IN_PRODUCTION":
            # Warn in development but don't block
            import warnings
            warnings.warn(
                "Using default SECRET_KEY. Generate a secure key for production: "
                "python -c \"import secrets; print(secrets.token_hex(32))\"",
                UserWarning
            )
        
        return v


# Initialize settings - this will raise an error if validation fails
try:
    settings = Settings()
except ValidationError as e:
    print(f"❌ Configuration Error: {e}")
    raise
