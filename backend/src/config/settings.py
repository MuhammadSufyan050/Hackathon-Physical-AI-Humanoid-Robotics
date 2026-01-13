import os
from typing import List, Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ValidationConfig(BaseModel):
    """
    Configuration parameters for the validation process
    """
    top_k: int = Field(default=5, description="Number of results to retrieve for each query")
    cohere_model: str = Field(default="embed-english-v3.0", description="Name of the Cohere model to use for embeddings")
    qdrant_collection: str = Field(default="rag_embedding", description="Name of the Qdrant collection to query")
    test_queries: List[str] = Field(default=["What is ROS2?", "Explain Gazebo simulation", "How to use Isaac Sim?"],
                                   description="List of predefined test queries to use")
    validation_threshold: float = Field(default=0.7, description="Minimum relevance score for acceptable results")
    max_retries: int = Field(default=3, description="Maximum number of retry attempts for failed queries")
    qdrant_host: str = Field(default="", description="Qdrant host URL")
    qdrant_api_key: str = Field(default="", description="Qdrant API key")
    qdrant_url: str = Field(default="", description="Qdrant URL (alternative to host)")
    cohere_api_key: str = Field(default="", description="Cohere API key")
    chunk_size: int = Field(default=1000, description="Size of text chunks")
    chunk_overlap: int = Field(default=200, description="Overlap between text chunks")


def get_config() -> ValidationConfig:
    """
    Get validation configuration from environment variables
    """
    return ValidationConfig(
        top_k=int(os.getenv("TOP_K", "5")),
        cohere_model=os.getenv("COHERE_MODEL", "embed-english-v3.0"),
        qdrant_collection=os.getenv("QDRANT_COLLECTION_NAME", "rag_embedding"),
        validation_threshold=float(os.getenv("VALIDATION_THRESHOLD", "0.7")),
        max_retries=int(os.getenv("MAX_RETRIES", "3")),
        qdrant_host=os.getenv("QDRANT_HOST", ""),
        qdrant_api_key=os.getenv("QDRANT_API_KEY", ""),
        qdrant_url=os.getenv("QDRANT_URL", ""),
        cohere_api_key=os.getenv("COHERE_API_KEY", ""),
        chunk_size=int(os.getenv("CHUNK_SIZE", "1000")),
        chunk_overlap=int(os.getenv("CHUNK_OVERLAP", "200"))
    )


# Global config instance
config = get_config()