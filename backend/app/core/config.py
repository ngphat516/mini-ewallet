from pydantic import Field, field_validator
from pydantic_settings import BaseSettings
from functools import lru_cache
from urllib.parse import quote_plus 


class Settings(BaseSettings):
    # ── SQL Server ─
    SQLSERVER_HOST: str
    SQLSERVER_PORT: int = 1433
    SQLSERVER_DB: str
    SQLSERVER_USER: str
    SQLSERVER_PASSWORD: str

    # ── MongoDB 
    MONGODB_URL: str
    MONGODB_DB: str

    # ── Redis 
    REDIS_URL: str

    # ── JWT 
    JWT_SECRET: str = Field(min_length=32)
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_EXPIRE_DAYS: int = 7

    # Comma-separated to keep Docker and local .env configuration simple.
    CORS_ORIGINS: str = "http://localhost:3000"

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }

    @field_validator("CORS_ORIGINS")
    @classmethod
    def cors_origins_must_not_be_empty(cls, value: str) -> str:
        origins = {origin.strip() for origin in value.split(",")}
        if not any(origins):
            raise ValueError("CORS_ORIGINS must contain at least one origin")
        if "*" in origins:
            raise ValueError("CORS_ORIGINS cannot contain '*' when credentials are enabled")
        return value

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip().rstrip("/") for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    @property
    def SQLSERVER_URL(self) -> str:
        return (
            f"mssql+pyodbc://{self.SQLSERVER_USER}:{quote_plus(self.SQLSERVER_PASSWORD)}"
            f"@{self.SQLSERVER_HOST}:{self.SQLSERVER_PORT}/{self.SQLSERVER_DB}"
            f"?driver=ODBC+Driver+18+for+SQL+Server"
            f"&TrustServerCertificate=yes"
            f"&Encrypt=yes"
        )

@lru_cache()
def get_settings() -> Settings:
    return Settings()

settings = get_settings()

