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
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 15
    JWT_REFRESH_EXPIRE_DAYS: int = 7

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": True,
    }

    

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

