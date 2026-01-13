"""Configuration management for Book Q&A Retrieval Agent."""

import os
from typing import Optional
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Application settings loaded from environment variables."""

    openai_api_key: str = Field(
        default=...,
        description="OpenAI API key for assistant operations"
    )
    cohere_api_key: str = Field(
        default=...,
        description="Cohere API key for embedding generation"
    )
    qdrant_url: str = Field(
        default=...,
        description="Qdrant Cloud endpoint URL"
    )
    qdrant_api_key: Optional[str] = Field(
        default=None,
        description="Qdrant API key for authentication (optional for local instances)"
    )
    qdrant_collection_name: str = Field(
        default="rag_embedding",
        description="Name of the Qdrant collection containing book content"
    )
    embedding_model: str = Field(
        default="embed-multilingual-v3.0",
        description="Cohere model to use for embeddings"
    )
    top_k_results: int = Field(
        default=5,
        description="Number of top results to retrieve from Qdrant"
    )
    min_score_threshold: float = Field(
        default=0.5,
        description="Minimum relevance score threshold for retrieved content"
    )
    max_query_length: int = Field(
        default=1000,
        description="Maximum length of user queries in characters"
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @classmethod
    def load_from_env(cls) -> "Settings":
        """Load settings from environment variables."""
        return cls(
            openai_api_key=os.getenv("OPENAI_API_KEY", ""),
            cohere_api_key=os.getenv("COHERE_API_KEY", ""),
            qdrant_url=os.getenv("QDRANT_URL", ""),
            qdrant_api_key=os.getenv("QDRANT_API_KEY"),
            qdrant_collection_name=os.getenv("QDRANT_COLLECTION_NAME", "rag_embedding"),
            embedding_model=os.getenv("EMBEDDING_MODEL", "embed-multilingual-v3.0"),
            top_k_results=int(os.getenv("TOP_K_RESULTS", "5")),
            min_score_threshold=float(os.getenv("MIN_SCORE_THRESHOLD", "0.5")),
            max_query_length=1000
        )


# Global settings instance
settings = Settings.load_from_env()


def validate_settings() -> bool:
    """Validate that all required settings are properly configured."""
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable is required")

    if not settings.cohere_api_key:
        raise ValueError("COHERE_API_KEY environment variable is required")

    if not settings.qdrant_url:
        raise ValueError("QDRANT_URL environment variable is required")

    if settings.top_k_results <= 0 or settings.top_k_results > 10:
        raise ValueError("TOP_K_RESULTS must be between 1 and 10")

    if settings.min_score_threshold < 0.0 or settings.min_score_threshold > 1.0:
        raise ValueError("MIN_SCORE_THRESHOLD must be between 0.0 and 1.0")

    return True