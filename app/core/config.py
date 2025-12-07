from typing import Optional, List, Any
from pydantic_settings import BaseSettings
from pydantic import PostgresDsn, SecretStr, validator
import os
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "Rovet API")
    VERSION: str = os.getenv("VERSION", "1.0.0")
    API_V1_STR: str = "/api/v1"
    
    # JWT Configuration
    # For RS256 (RSA): Use JWT_PRIVATE_KEY and JWT_PUBLIC_KEY
    # For HS256 (HMAC): Use SECRET_KEY (legacy, not recommended for microservices)
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-here")  # Legacy, for HS256
    JWT_PRIVATE_KEY: Optional[str] = os.getenv("JWT_PRIVATE_KEY")  # RSA private key for signing
    JWT_PUBLIC_KEY: Optional[str] = os.getenv("JWT_PUBLIC_KEY")  # RSA public key for verification
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "RS256")  # RS256 for microservices, HS256 for legacy
    JWT_ISSUER: str = os.getenv("JWT_ISSUER", "rovet-auth-service")  # Token issuer (iss claim)
    JWT_AUDIENCE: str = os.getenv("JWT_AUDIENCE", "rovet-services")  # Token audience (aud claim)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", "7"))
    
    PORT: int = int(os.getenv("PORT", "8001"))
    
    # Environment detection
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Database configuration
    POSTGRES_SERVER: str = os.getenv("POSTGRES_SERVER", "db")
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: SecretStr = SecretStr(os.getenv("POSTGRES_PASSWORD", "postgres"))
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "app_db")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    
    # Direct database URL for production (Neon DB)
    DATABASE_URL: Optional[str] = os.getenv("DATABASE_URL")
    
    BACKEND_CORS_ORIGINS: List[str] = eval(os.getenv("BACKEND_CORS_ORIGINS", '["http://localhost:8001"]'))
    
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    DEFAULT_PAGE_SIZE: int = 10
    MAX_PAGE_SIZE: int = 100

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: dict) -> Any:
        # If DATABASE_URL is provided (production), use it directly
        if values.get("DATABASE_URL"):
            print(f"Using production database URL: {values.get('DATABASE_URL')[:50]}...")
            return values.get("DATABASE_URL")
        
        # Otherwise, build from individual components (development)
        if isinstance(v, str):
            return v
        
        db_name = values.get("POSTGRES_DB")
        print(f"Building database URI for development: {values.get('POSTGRES_SERVER')}:{values.get('POSTGRES_PORT')}/{db_name}")
        
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD").get_secret_value(),
            host=values.get("POSTGRES_SERVER"),
            port=int(values.get("POSTGRES_PORT")),
            path=db_name,
        )

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings() 