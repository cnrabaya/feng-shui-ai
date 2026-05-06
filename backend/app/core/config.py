from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Resolve the root directory of the project (3 levels up from core/config.py)
ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent

class Settings(BaseSettings):
    app_name: str = "FengShuiAI"
    app_version: str = "0.1.0"
    cors_origins: list[str] = ["http://localhost:5173"]
    vllm_base_url: str = "http://127.0.0.1:8000/v1/chat/completions"
    model_name: str = "Qwen/Qwen3-VL-235B-A22B-Instruct"
    qwen_vl_api_key: str = "EMPTY"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=str(ROOT_DIR / ".env"), env_file_encoding="utf-8")


settings = Settings()