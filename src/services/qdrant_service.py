"""Qdrant service for vector database operations."""

from typing import List, Dict, Any, Optional
from qdrant_client import QdrantClient
from qdrant_client.http import models
from qdrant_client.http.models import PointStruct, VectorParams, Distance
from src.config.settings import settings
import logging


logger = logging.getLogger(__name__)


class QdrantService:
    """Service class for interacting with Qdrant vector database."""

    def __init__(self):
        """Initialize Qdrant client with configuration."""
        self.client = QdrantClient(
            url=settings.qdrant_url,
            api_key=settings.qdrant_api_key,
            timeout=30
        )
        self.collection_name = settings.qdrant_collection_name

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        min_score: float = 0.5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for similar content in Qdrant collection.

        Args:
            query_vector: The embedding vector to search for
            top_k: Number of results to return
            min_score: Minimum relevance score threshold
            filters: Optional filters to apply to the search

        Returns:
            List of matching documents with metadata
        """
        try:
            # Prepare filters if provided
            search_filter = None
            if filters:
                conditions = []
                for key, value in filters.items():
                    conditions.append(
                        models.FieldCondition(
                            key=key,
                            match=models.MatchValue(value=value)
                        )
                    )

                if conditions:
                    search_filter = models.Filter(
                        must=conditions
                    )

            # Perform search
            search_results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                limit=top_k,
                score_threshold=min_score,
                query_filter=search_filter
            )

            # Format results
            formatted_results = []
            for result in search_results:
                formatted_result = {
                    "id": result.id,
                    "content": result.payload.get("content", ""),
                    "score": result.score,
                    "source_url": result.payload.get("source_url"),
                    "page_number": result.payload.get("page_number"),
                    "section_title": result.payload.get("section_title"),
                    "metadata": result.payload
                }
                formatted_results.append(formatted_result)

            logger.info(f"Found {len(formatted_results)} results for query")
            return formatted_results

        except Exception as e:
            logger.error(f"Error searching Qdrant: {str(e)}")
            raise

    def get_point(self, point_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a specific point by ID from the collection.

        Args:
            point_id: The ID of the point to retrieve

        Returns:
            Point data with metadata or None if not found
        """
        try:
            points = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[point_id]
            )

            if points:
                point = points[0]
                return {
                    "id": point.id,
                    "content": point.payload.get("content", ""),
                    "source_url": point.payload.get("source_url"),
                    "page_number": point.payload.get("page_number"),
                    "section_title": point.payload.get("section_title"),
                    "metadata": point.payload
                }

            return None
        except Exception as e:
            logger.error(f"Error retrieving point {point_id} from Qdrant: {str(e)}")
            raise

    def verify_connection(self) -> bool:
        """
        Verify connection to Qdrant and check if collection exists.

        Returns:
            True if connection is successful and collection exists
        """
        try:
            # Try to get collection info
            collection_info = self.client.get_collection(self.collection_name)
            logger.info(f"Successfully connected to Qdrant collection: {self.collection_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to Qdrant collection {self.collection_name}: {str(e)}")
            return False

    def count_points(self) -> int:
        """
        Get the total number of points in the collection.

        Returns:
            Total number of points in the collection
        """
        try:
            count_result = self.client.count(
                collection_name=self.collection_name
            )
            return count_result.count
        except Exception as e:
            logger.error(f"Error counting points in Qdrant: {str(e)}")
            raise