from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- Google Gemini ---
    google_api_key: str
    gemini_llm_model: str = "gemini-2.5-flash"
    gemini_embedding_model: str = "models/gemini-embedding-001"
    embedding_dimensions: int = 768

    # --- Pinecone ---
    pinecone_api_key: str
    pinecone_index_name: str = "ai-knowledge-inbox"
    pinecone_cloud: str = "aws"
    pinecone_region: str = "us-east-1"

    # --- Chunking ---
    chunk_size_words: int = 220
    chunk_overlap_words: int = 40

    # --- Retrieval ---
    default_top_k: int = 3

    # --- App ---
    sqlite_db_path: str = "./data/app.db"
    log_level: str = "INFO"
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @property
    def cors_origin_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()
