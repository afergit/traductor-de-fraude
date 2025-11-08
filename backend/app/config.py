from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    ENV: str = "dev"
    ALLOW_ORIGINS: str = "*" 
    PORT: int = 8000
    IA_API_KEY: str | None = None

    class Config:
        env_file = ".env"
        extra = "ignore"

def get_cors_origins(cfg: Settings) -> List[str]:
    if cfg.ALLOW_ORIGINS.strip() == "*":
        return ["*"]
    return [o.strip() for o in cfg.ALLOW_ORIGINS.split(",") if o.strip()]
