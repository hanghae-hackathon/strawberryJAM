import os.path

from pydantic_settings import BaseSettings, SettingsConfigDict


class ConfigTemplate(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=os.path.expandvars(".env"),
        env_file_encoding="utf-8",
        env_prefix="APP_",
    )

    @property
    def db_uri(self) -> str:
        return "sqlite+aiosqlite:///./sql_app.db"


config = ConfigTemplate()


def get_config() -> ConfigTemplate:
    return config
