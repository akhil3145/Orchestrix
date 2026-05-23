"""Simple runtime diagnostics for Orchestrix."""
from typing import List
from app.config import settings


def validate_env() -> List[str]:
    warnings = []
    if not settings.anthropic_api_key:
        warnings.append("ANTHROPIC_API_KEY is not set — chat assistant will fall back to local answers.")
    if not settings.pinecone_api_key:
        warnings.append("PINECONE_API_KEY is not set — vector search and RAG features disabled.")
    if not settings.ollama_base_url:
        warnings.append("OLLAMA_BASE_URL is not set — local Ollama fallback may be unavailable.")
    # data files
    if not settings.data_path:
        warnings.append("EMPLOYEE_DATA_PATH is not configured — employee features may fail.")
    return warnings
