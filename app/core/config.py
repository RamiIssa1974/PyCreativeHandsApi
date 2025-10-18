from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # App
    APP_NAME: str = "PyCreativeHandsApi"
    ENV: str = "dev"
    API_PREFIX: str = ""

    # Data provider selector: sql | mongo | redis | http
    DATA_PROVIDER: str = "sql"

    # SQL Server
    SQLSERVER_HOST: str = "localhost"
    SQLSERVER_DB: str = "master"
    SQLSERVER_USER: str = "sa"
    SQLSERVER_PASSWORD: str = ""
    SQL_ODBC_DRIVER: str = "ODBC Driver 17 for SQL Server"
    SQL_TRUST_CERT: str = "true"  # "true" or "false"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False)


@lru_cache
def get_settings() -> Settings:
    # cached singleton; fast and thread-safe
    return Settings()
