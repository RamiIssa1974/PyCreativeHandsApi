from functools import lru_cache
from typing import ClassVar, Optional
from pydantic import Field

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

    FTP_HOST: Optional[str] = "194.36.89.39"
    FTP_USER: Optional[str] = "FtpUser"
    FTP_PASS: Optional[str] = "creativeHands2024!"
    # optional
    #FTP_BASE_DIR=your/base/dir   
    APP_NAME: ClassVar[str] = "PyCreativeHandsApi"
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=False,
    )

    jwt_secret: Optional[str] = Field(default=None, alias="Authentication__JwtSecret")
    auth_issuer: str = Field(default="PyCreativeHandsApi", alias="Authentication__Issuer")
    auth_audience: str = Field(default="CreativeHandsClients", alias="Authentication__Audience")

_settings: Optional[Settings] = None

@lru_cache
def get_settings() -> Settings:
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings

