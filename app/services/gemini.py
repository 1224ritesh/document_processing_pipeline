from functools import lru_cache

from google import genai
from google.genai import types
from app.config import get_settings


@lru_cache(maxsize=1)
def get_gemini_client() -> genai.Client:
    settings = get_settings()
    return genai.Client(api_key=settings.gemini_api_key)


def make_pdf_part(pdf_bytes: bytes) -> types.Part:
    return types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")
