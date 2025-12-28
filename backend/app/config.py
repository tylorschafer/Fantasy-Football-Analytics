from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Fantasy Football League Analyzer"
    app_version: str = "0.1.0"
    debug: bool = False
    api_prefix: str = "/api/v1"


settings = Settings()
