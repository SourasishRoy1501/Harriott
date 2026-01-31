"""
Configuration settings for Harriot SOA
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Supabase
    supabase_url: str
    supabase_key: str
    
    # OpenAI
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"

    gemini_model: str = "gemini-2.5-flash"
    gemini_api_key: str
    
    # LangSmith (optional)
    langchain_tracing_v2: bool = False
    langchain_api_key: Optional[str] = None
    langchain_project: str = "harriot-soa"
    
    # Application
    environment: str = "development"
    log_level: str = "INFO"
    
    # Analysis parameters
    default_lookback_days: int = 30
    confidence_threshold: float = 0.70
    
    # Temperature settings for LLM
    llm_temperature: float = 0.2
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )


# Singleton instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create settings instance"""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
