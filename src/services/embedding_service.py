"""Cohere embedding service for generating vector embeddings."""

import cohere
from typing import List
from src.config.settings import settings
import logging


logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service class for generating embeddings using Cohere API."""

    def __init__(self):
        """Initialize Cohere client with configuration."""
        self.client = cohere.Client(settings.cohere_api_key)
        self.model = settings.embedding_model

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: The text to generate embedding for

        Returns:
            List of floats representing the embedding vector
        """
        if len(text) > settings.max_query_length:
            raise ValueError(f"Text exceeds maximum length of {settings.max_query_length} characters")

        try:
            response = self.client.embed(
                texts=[text],
                model=self.model
            )

            if not response.embeddings:
                raise ValueError("No embeddings returned from Cohere API")

            embedding = response.embeddings[0]
            logger.info(f"Generated embedding for text of length {len(text)}")
            return embedding

        except Exception as e:
            logger.error(f"Error generating embedding: {str(e)}")
            raise

    def generate_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for multiple texts.

        Args:
            texts: List of texts to generate embeddings for

        Returns:
            List of embedding vectors (each vector is a list of floats)
        """
        # Check length constraints
        for text in texts:
            if len(text) > settings.max_query_length:
                raise ValueError(f"Text exceeds maximum length of {settings.max_query_length} characters")

        try:
            response = self.client.embed(
                texts=texts,
                model=self.model
            )

            if not response.embeddings:
                raise ValueError("No embeddings returned from Cohere API")

            embeddings = response.embeddings
            logger.info(f"Generated embeddings for {len(texts)} texts")
            return embeddings

        except Exception as e:
            logger.error(f"Error generating embeddings: {str(e)}")
            raise

    def get_embedding_dimensions(self) -> int:
        """
        Get the dimension of embeddings for the configured model.

        Returns:
            Number of dimensions in the embedding vectors
        """
        # Generate a simple test embedding to determine dimensions
        test_embedding = self.generate_embedding("test")
        return len(test_embedding)

    def validate_text_for_embedding(self, text: str) -> bool:
        """
        Validate if text is appropriate for embedding generation.

        Args:
            text: The text to validate

        Returns:
            True if text is valid for embedding, False otherwise
        """
        if not text or not text.strip():
            return False

        if len(text) > settings.max_query_length:
            return False

        return True