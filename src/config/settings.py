from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """
    Application Settings managed by Pydantic.
    Reads from environment variables and .env file.
    """

    # Database
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "password"
    DB_NAME: str = "ai_newsletter"
    DB_HOST: str = "localhost"
    DB_PORT: int = 5432

    # YouTube / LLM
    GROQ_API_KEY: Optional[str] = None
    GEMINI_API_KEY: Optional[str] = None

    # Ollama (Local LLM)
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "gemma3:4b"

    # Rate Limiting
    MAX_VIDEOS_PER_RUN: int = 5

    @property
    def DB_URL(self) -> str:
        """Constructs the database connection URL."""
        return f"postgresql+psycopg2://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra env vars


settings = Settings()
