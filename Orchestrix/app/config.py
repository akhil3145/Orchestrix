"""Runtime configuration for Orchestrix."""

from dataclasses import dataclass
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from Orchestrix directory
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(env_path)


@dataclass(frozen=True)
class Settings:
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    pinecone_api_key: str = os.getenv("PINECONE_API_KEY", "")
    pinecone_environment: str = os.getenv("PINECONE_ENVIRONMENT", "us-east-1")
    pinecone_index_name: str = os.getenv("PINECONE_INDEX_NAME", "tk-policy")
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    default_model: str = os.getenv("DEFAULT_MODEL", "gemini")
    rate_limit_rpm: int = int(os.getenv("RATE_LIMIT_RPM", "20"))
    enable_sentiment: bool = os.getenv("ENABLE_SENTIMENT", "true").lower() == "true"
    enable_translation: bool = os.getenv("ENABLE_TRANSLATION", "true").lower() == "true"
    audit_log_path: str = os.getenv("AUDIT_LOG_PATH", "logs/audit.jsonl")
    data_path: str = os.getenv("EMPLOYEE_DATA_PATH", "employee_data.csv")
    policy_path: str = os.getenv("HR_POLICY_PATH", "hr_policy.txt")
    candidate_db_path: str = os.getenv("CANDIDATE_DB_PATH", "data/candidates.db")


settings = Settings()
