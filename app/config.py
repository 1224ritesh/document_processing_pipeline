from pydantic_settings import BaseSettings
from functools import lru_cache
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = "Document Processing Pipeline"
    debug: bool = False

    # Gemini
    gemini_api_key: str = Field(..., min_length=1)
    segregator_model: str = "gemini-2.5-flash-lite"
    extractor_model: str = "gemini-2.5-flash"

    # PDF processing
    max_pdf_size_mb: int = 50
    max_pdf_pages: int = 1000

    # Rate limiting
    rate_limit: str = "3/minute"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
