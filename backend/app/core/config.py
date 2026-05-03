from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name: str = "FengShuiAI"
    app_version: str = "0.1.0"
    cors_origins: list[str] = ["http://localhost:5173"]


settings = Settings()