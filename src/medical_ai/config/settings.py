from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    """Runtime settings loaded from environment variables and optional .env."""

    mysql_host: str = "127.0.0.1"
    mysql_port: int = 3306
    mysql_database: str = "medical_ai"
    mysql_user: str = "medical_ai"
    mysql_password: str = Field(default="", repr=False)

    query_default_limit: int = 100
    query_max_limit: int = 1000
    query_max_distinct_values: int = 200
    query_timeout_ms: int = 30000

    mcp_transport: Literal["stdio", "sse", "streamable-http"] = "stdio"
    mcp_host: str = "127.0.0.1"
    mcp_port: int = 3001

    llm_base_url: str = ""
    llm_api_key: str = Field(default="", repr=False)
    llm_model: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    def mysql_url(self) -> URL:
        return URL.create(
            "mysql+pymysql",
            username=self.mysql_user,
            password=self.mysql_password,
            host=self.mysql_host,
            port=self.mysql_port,
            database=self.mysql_database,
            query={"charset": "utf8mb4"},
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()
