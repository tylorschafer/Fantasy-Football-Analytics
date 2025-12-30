from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

# Define the backend directory root
BACKEND_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BACKEND_DIR / "data"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Fantasy Football League Analyzer"
    app_version: str = "0.1.0"
    debug: bool = False
    api_prefix: str = "/api/v1"

    # Database configuration
    database_url: str = f"sqlite+aiosqlite:///{DATA_DIR}/app.db"
    database_echo: bool = False  # Set to True to log SQL queries


settings = Settings()
