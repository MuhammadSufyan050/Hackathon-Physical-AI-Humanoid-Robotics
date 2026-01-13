"""Qdrant retrieval tool for the Book Q&A Agent."""

import json
import logging
from typing import Dict, Any, List
from src.services.qdrant_service import QdrantService
from src.services.embedding_service import EmbeddingService
from src.config.settings import settings
from src.utils.error_handler import AgentError, RetrievalError


logger = logging.getLogger(__name__)


class RetrievalTool:
    """Tool for retrieving relevant content from Qdrant based on semantic similarity."""

    def __init__(self):
        """Initialize the retrieval tool with required services."""
        self.qdrant_service = QdrantService()
        self.embedding_service = EmbeddingService()

    def get_name(self) -> str:
        """Get the name of the tool."""
        return "retrieve_book_content"

    def get_description(self) -> str:
        """Get the description of the tool."""
        return "Retrieve relevant content from book collection based on semantic similarity to the user's query"

    def get_parameters(self) -> Dict[str, Any]:
        """Get the parameters schema for the tool."""
        return {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The user's question or query to search for relevant content"
                },
                "top_k": {
                    "type": "number",
                    "description": "Number of top results to return (default: 5, max: 10)",
                    "default": 5,
                    "minimum": 1,
                    "maximum": 10
                },
                "min_score": {
                    "type": "number",
                    "description": "Minimum relevance score threshold (default: 0.5, range: 0.0-1.0)",
                    "default": 0.5,
                    "minimum": 0.0,
                    "maximum": 1.0
                }
            },
            "required": ["query"]
        }

    def run(self, tool_input: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the retrieval tool with the given input.

        Args:
            tool_input: Dictionary containing query, top_k, and min_score parameters

        Returns:
            Dictionary with retrieval results
        """
        try:
            query = tool_input.get("query")
            if not query:
                raise RetrievalError("Query parameter is required")

            # Get top_k and min_score with defaults
            top_k = tool_input.get("top_k", settings.top_k_results)
            min_score = tool_input.get("min_score", settings.min_score_threshold)

            # Validate parameters
            if not isinstance(top_k, int) or top_k < 1 or top_k > 10:
                raise RetrievalError("top_k must be an integer between 1 and 10", query=query)

            if not isinstance(min_score, (int, float)) or min_score < 0.0 or min_score > 1.0:
                raise RetrievalError("min_score must be a number between 0.0 and 1.0", query=query)

            # Generate embedding for the query
            query_embedding = self.embedding_service.generate_embedding(query)

            # Search in Qdrant
            results = self.qdrant_service.search(
                query_vector=query_embedding,
                top_k=top_k,
                min_score=min_score
            )

            # Format results according to the contract
            formatted_results = []
            for result in results:
                formatted_result = {
                    "id": result["id"],
                    "content": result["content"],
                    "score": result["score"],
                    "source_url": result.get("source_url"),
                    "page_number": result.get("page_number"),
                    "section_title": result.get("section_title"),
                    "metadata": result.get("metadata", {})
                }
                formatted_results.append(formatted_result)

            response = {
                "results": formatted_results,
                "query_embedding_used": query_embedding
            }

            logger.info(f"Retrieved {len(formatted_results)} results for query: {query[:50]}...")
            return response

        except RetrievalError:
            # Re-raise retrieval errors as they're already properly formatted
            raise
        except Exception as e:
            logger.error(f"Error in retrieval tool: {str(e)}")
            raise RetrievalError(f"Failed to retrieve content: {str(e)}", query=tool_input.get("query"))

    def register_with_assistant(self) -> Dict[str, Any]:
        """
        Get the tool definition in the format expected by OpenAI Assistant API.

        Returns:
            Tool definition dictionary
        """
        return {
            "type": "function",
            "function": {
                "name": self.get_name(),
                "description": self.get_description(),
                "parameters": self.get_parameters()
            }
        }

    def validate_query(self, query: str) -> bool:
        """
        Validate the query before processing.

        Args:
            query: The query string to validate

        Returns:
            True if query is valid, raises exception if not
        """
        if not query or not query.strip():
            raise RetrievalError("Query cannot be empty")

        if len(query) < 3:
            raise RetrievalError("Query must be at least 3 characters long")

        if len(query) > settings.max_query_length:
            raise RetrievalError(f"Query exceeds maximum length of {settings.max_query_length} characters")

        return True