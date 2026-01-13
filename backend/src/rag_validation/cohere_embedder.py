import cohere
import logging
import time
from typing import List
from ..config.settings import config

logger = logging.getLogger(__name__)


class CohereEmbedder:
    """
    Generates embeddings for queries using Cohere API
    Ensures consistency with the embedding model used during indexing
    """

    def __init__(self):
        """
        Initialize Cohere client with API key from configuration
        """
        if not config.cohere_api_key:
            raise ValueError("COHERE_API_KEY environment variable must be set")

        self.client = cohere.Client(config.cohere_api_key)
        self.model = config.cohere_model

    def embed_text(self, text: str) -> List[float]:
        """
        Generate embedding for a single text string
        """
        logger.debug(f"Generating embedding for text: {text[:50]}...")
        start_time = time.time()
        max_retries = config.max_retries
        last_error = None

        for attempt in range(max_retries):
            try:
                response = self.client.embed(
                    texts=[text],
                    model=self.model,
                    input_type="search_query"  # Using search_query for queries
                )
                embedding_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                logger.info(f"Successfully generated embedding for text of length {len(text)} in {embedding_time:.2f}ms")
                return response.embeddings[0]  # Return the first (and only) embedding

            except cohere.CohereAPIError as e:
                last_error = e
                embedding_time = (time.time() - start_time) * 1000
                if "rate limit" in str(e).lower():
                    logger.warning(f"Cohere rate limit hit on attempt {attempt + 1} after {embedding_time:.2f}ms, backing off...")
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.warning(f"Cohere API error on attempt {attempt + 1} after {embedding_time:.2f}ms: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(1 * (attempt + 1))  # Linear backoff for other errors
                    break  # Don't retry for other API errors
            except Exception as e:
                last_error = e
                embedding_time = (time.time() - start_time) * 1000
                logger.warning(f"Cohere embedding attempt {attempt + 1} failed after {embedding_time:.2f}ms: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1 * (attempt + 1))
                else:
                    logger.error(f"Cohere embedding failed after {max_retries} attempts: {e}")

        # If all retries failed, raise the last error
        raise last_error

    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Generate embeddings for a list of text strings
        """
        logger.debug(f"Generating embeddings for {len(texts)} texts")
        start_time = time.time()
        max_retries = config.max_retries
        last_error = None

        for attempt in range(max_retries):
            try:
                response = self.client.embed(
                    texts=texts,
                    model=self.model,
                    input_type="search_document"  # Using search_document for documents
                )
                embedding_time = (time.time() - start_time) * 1000  # Convert to milliseconds
                logger.info(f"Successfully generated {len(response.embeddings)} embeddings for {len(texts)} texts in {embedding_time:.2f}ms")
                return response.embeddings

            except cohere.CohereAPIError as e:
                last_error = e
                embedding_time = (time.time() - start_time) * 1000
                if "rate limit" in str(e).lower():
                    logger.warning(f"Cohere rate limit hit on attempt {attempt + 1} after {embedding_time:.2f}ms, backing off...")
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    logger.warning(f"Cohere API error on attempt {attempt + 1} after {embedding_time:.2f}ms: {e}")
                    if attempt < max_retries - 1:
                        time.sleep(1 * (attempt + 1))  # Linear backoff for other errors
                    break  # Don't retry for other API errors
            except Exception as e:
                last_error = e
                embedding_time = (time.time() - start_time) * 1000
                logger.warning(f"Cohere batch embedding attempt {attempt + 1} failed after {embedding_time:.2f}ms: {e}")
                if attempt < max_retries - 1:
                    time.sleep(1 * (attempt + 1))
                else:
                    logger.error(f"Cohere batch embedding failed after {max_retries} attempts: {e}")

        # If all retries failed, raise the last error
        raise last_error

    def embed_query(self, query: str) -> List[float]:
        """
        Generate embedding for a query (alias for embed_text with semantic meaning)
        """
        return self.embed_text(query)

    def get_model_info(self) -> dict:
        """
        Get information about the embedding model being used
        """
        return {
            "model": self.model,
            "api_key_set": bool(config.cohere_api_key)
        }