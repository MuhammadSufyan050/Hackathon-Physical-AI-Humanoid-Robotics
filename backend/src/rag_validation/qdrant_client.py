import logging
from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import PointStruct
from ..config.settings import config
from .entities import TextChunk
import time

logger = logging.getLogger(__name__)


class QdrantClientWrapper:
    """
    Wrapper for Qdrant client to handle connection and queries to Qdrant Cloud
    Manages connection pooling and error handling
    """

    def __init__(self):
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize Qdrant client based on configuration"""
        try:
            if config.qdrant_url:
                # Use URL if provided
                self.client = QdrantClient(
                    url=config.qdrant_url,
                    api_key=config.qdrant_api_key,
                    timeout=10.0
                )
            elif config.qdrant_host:
                # Use host if URL not provided
                self.client = QdrantClient(
                    host=config.qdrant_host,
                    api_key=config.qdrant_api_key,
                    timeout=10.0
                )
            else:
                raise ValueError("Either QDRANT_URL or QDRANT_HOST must be provided in configuration")

            logger.info("Qdrant client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Qdrant client: {e}")
            raise

    def validate_connection(self) -> bool:
        """
        Validate connection to Qdrant Cloud
        Returns True if connection is successful, False otherwise
        """
        start_time = time.time()
        try:
            # Try to list collections as a basic connectivity test
            collections = self.client.get_collections()
            connection_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            logger.info(f"Qdrant connection validated successfully in {connection_time:.2f}ms")
            logger.debug(f"Available collections: {[col.name for col in collections.collections]}")
            return True
        except Exception as e:
            logger.error(f"Qdrant connection validation failed: {e}")
            return False

    def safe_search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Safely execute semantic search with error handling and retries
        """
        max_retries = config.max_retries
        last_error = None

        for attempt in range(max_retries):
            try:
                # Perform the search
                search_results = self.client.search(
                    collection_name=config.qdrant_collection,
                    query_vector=query_vector,
                    limit=top_k,
                    with_payload=True,
                    with_vectors=False
                )

                # Format results
                formatted_results = []
                for result in search_results:
                    formatted_result = {
                        'id': result.id,
                        'content': result.payload.get('content', ''),
                        'metadata': result.payload.get('metadata', {}),
                        'similarity_score': result.score
                    }
                    formatted_results.append(formatted_result)

                logger.info(f"Successfully retrieved {len(formatted_results)} results from Qdrant")
                return formatted_results

            except Exception as e:
                last_error = e
                logger.warning(f"Qdrant search attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:  # Don't sleep on the last attempt
                    time.sleep(0.5 * (attempt + 1))  # Exponential backoff
                else:
                    logger.error(f"Qdrant search failed after {max_retries} attempts: {e}")

        # If all retries failed, raise the last error
        raise last_error

    def search(self, query_vector: List[float], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Execute semantic search in Qdrant and return top-k results
        """
        start_time = time.time()
        try:
            results = self.safe_search(query_vector, top_k)
            search_time = (time.time() - start_time) * 1000  # Convert to milliseconds
            logger.info(f"Qdrant search completed in {search_time:.2f}ms for top-{top_k} results")
            logger.debug(f"Retrieved {len(results)} results from Qdrant search")
            return results
        except Exception as e:
            search_time = (time.time() - start_time) * 1000
            logger.error(f"Qdrant search failed after {search_time:.2f}ms: {e}")
            raise

    def get_point(self, point_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific point by ID from Qdrant
        """
        try:
            points = self.client.retrieve(
                collection_name=config.qdrant_collection,
                ids=[point_id],
                with_payload=True,
                with_vectors=False
            )

            if points:
                point = points[0]
                return {
                    'id': point.id,
                    'content': point.payload.get('content', ''),
                    'metadata': point.payload.get('metadata', {}),
                }
            return None
        except Exception as e:
            logger.error(f"Failed to retrieve point {point_id} from Qdrant: {e}")
            return None

    def close(self):
        """Close the Qdrant client connection"""
        if self.client:
            # QdrantClient doesn't have a close method, but we can set it to None
            self.client = None


# Global instance of Qdrant client
qdrant_client = QdrantClientWrapper()