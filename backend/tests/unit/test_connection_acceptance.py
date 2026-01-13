import time
import pytest
from unittest.mock import patch
from src.rag_validation.api import test_connection


class TestConnectionAcceptance:
    """Acceptance tests for connection functionality"""

    @patch('src.rag_validation.qdrant_client.QdrantClient')
    def test_connection_established_within_10_seconds(self, mock_qdrant_client):
        """Test that connection is established within 10 seconds (acceptance criteria)"""
        # Mock the client instance and its methods
        mock_client_instance = mock_qdrant_client.return_value
        mock_client_instance.get_collections.return_value = ['test-collection']

        # Record start time
        start_time = time.time()

        # Test the connection
        result = test_connection()

        # Calculate elapsed time
        elapsed_time = time.time() - start_time

        # Assertions
        assert result["success"] is True
        assert "Successfully connected to Qdrant Cloud" in result["message"]
        assert result["response_time_ms"] > 0
        assert elapsed_time < 10.0, f"Connection took {elapsed_time:.2f}s, which is more than 10 seconds"
        assert result["response_time_ms"] < 10000, f"Response time was {result['response_time_ms']}ms, which is more than 10000ms (10 seconds)"

    @patch('src.rag_validation.qdrant_client.QdrantClient')
    def test_connection_failed_case(self, mock_qdrant_client):
        """Test connection failure handling"""
        # Mock the client instance to raise an exception
        mock_client_instance = mock_qdrant_client.return_value
        mock_client_instance.get_collections.side_effect = Exception("Connection failed")

        # Test the connection
        result = test_connection()

        # Assertions
        assert result["success"] is False
        assert "Failed to connect to Qdrant Cloud" in result["error"]
        assert result["response_time_ms"] > 0