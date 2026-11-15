from functools import lru_cache

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    app_name: str = "HealthCare"
    app_version: str = "0.1.0"
    environment: str = "development"
    debug: bool = True

    database_url: str = "sqlite:///./orbitcare.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    @field_validator("debug", mode="before")
    @classmethod
    def parse_debug(cls, value):
        """Some machines have a global DEBUG=release variable that is not a
        boolean; ignore values pydantic cannot interpret."""
        if isinstance(value, str) and value.strip().lower() not in (
            "true", "false", "1", "0", "yes", "no", "on", "off",
        ):
            return True
        return value


@lru_cache
def get_settings() -> Settings:

    return Settings()


settings = get_settings()
