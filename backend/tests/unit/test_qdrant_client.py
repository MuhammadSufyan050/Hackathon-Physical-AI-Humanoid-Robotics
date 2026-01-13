import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from src.rag_validation.qdrant_client import QdrantClientWrapper
from src.config.settings import config


class TestQdrantClientWrapper:
    """Unit tests for QdrantClientWrapper"""

    def setup_method(self):
        """Set up test fixtures before each test method"""
        # Mock environment variables
        os.environ['QDRANT_HOST'] = 'test-host'
        os.environ['QDRANT_API_KEY'] = 'test-key'
        os.environ['QDRANT_COLLECTION_NAME'] = 'test-collection'

        # Reload config to pick up new environment variables
        import importlib
        importlib.reload(config)

    @patch('src.rag_validation.qdrant_client.QdrantClient')
    def test_initialize_client_with_url(self, mock_qdrant_client):
        """Test initializing client with URL configuration"""
        # Set up environment
        os.environ['QDRANT_URL'] = 'https://test.qdrant.tech:6333'
        os.environ['QDRANT_API_KEY'] = 'test-key'
        os.environ['QDRANT_COLLECTION_NAME'] = 'test-collection'

        # Reload config
        import importlib
        importlib.reload(config)

        # Initialize client
        client_wrapper = QdrantClientWrapper()

        # Verify QdrantClient was called with URL
        mock_qdrant_client.assert_called_once()
        args, kwargs = mock_qdrant_client.call_args
        assert kwargs.get('url') == 'https://test.qdrant.tech:6333'
        assert kwargs.get('api_key') == 'test-key'

    @patch('src.rag_validation.qdrant_client.QdrantClient')
    def test_initialize_client_with_host(self, mock_qdrant_client):
        """Test initializing client with host configuration"""
        # Set up environment
        os.environ.pop('QDRANT_URL', None)  # Remove URL to use host
        os.environ['QDRANT_HOST'] = 'test-host'
        os.environ['QDRANT_API_KEY'] = 'test-key'
        os.environ['QDRANT_COLLECTION_NAME'] = 'test-collection'

        # Reload config
        import importlib
        importlib.reload(config)

        # Initialize client
        client_wrapper = QdrantClientWrapper()

        # Verify QdrantClient was called with host
        mock_qdrant_client.assert_called_once()
        args, kwargs = mock_qdrant_client.call_args
        assert kwargs.get('host') == 'test-host'
        assert kwargs.get('api_key') == 'test-key'

    @patch('src.rag_validation.qdrant_client.QdrantClient')
    def test_validate_connection_success(self, mock_qdrant_client):
        """Test successful connection validation"""
        # Mock the client instance and its methods
        mock_client_instance = Mock()
        mock_client_instance.get_collections.return_value = ['test-collection']
        mock_qdrant_client.return_value = mock_client_instance

        # Set up environment
        os.environ['QDRANT_HOST'] = 'test-host'
        os.environ['QDRANT_API_KEY'] = 'test-key'
        os.environ['QDRANT_COLLECTION_NAME'] = 'test-collection'

        # Reload config
        import importlib
        importlib.reload(config)

        # Initialize client
        client_wrapper = QdrantClientWrapper()

        # Test the validation
        result = client_wrapper.validate_connection()

        # Assertions
        assert result is True
        mock_client_instance.get_collections.assert_called_once()

    @patch('src.rag_validation.qdrant_client.QdrantClient')
    def test_validate_connection_failure(self, mock_qdrant_client):
        """Test failed connection validation"""
        # Mock the client instance to raise an exception
        mock_client_instance = Mock()
        mock_client_instance.get_collections.side_effect = Exception("Connection failed")
        mock_qdrant_client.return_value = mock_client_instance

        # Set up environment
        os.environ['QDRANT_HOST'] = 'test-host'
        os.environ['QDRANT_API_KEY'] = 'test-key'
        os.environ['QDRANT_COLLECTION_NAME'] = 'test-collection'

        # Reload config
        import importlib
        importlib.reload(config)

        # Initialize client
        client_wrapper = QdrantClientWrapper()

        # Test the validation
        result = client_wrapper.validate_connection()

        # Assertions
        assert result is False

    @patch('src.rag_validation.qdrant_client.QdrantClient')
    def test_search_method(self, mock_qdrant_client):
        """Test the search method"""
        # Mock search results
        mock_search_result = [
            Mock(id='point1', payload={'content': 'test content', 'metadata': {'url': 'test.com'}}, score=0.9)
        ]

        mock_client_instance = Mock()
        mock_client_instance.search.return_value = mock_search_result
        mock_qdrant_client.return_value = mock_client_instance

        # Set up environment
        os.environ['QDRANT_HOST'] = 'test-host'
        os.environ['QDRANT_API_KEY'] = 'test-key'
        os.environ['QDRANT_COLLECTION_NAME'] = 'test-collection'

        # Reload config
        import importlib
        importlib.reload(config)

        # Initialize client
        client_wrapper = QdrantClientWrapper()

        # Test the search
        results = client_wrapper.search([0.1, 0.2, 0.3], top_k=1)

        # Assertions
        assert len(results) == 1
        assert results[0]['id'] == 'point1'
        assert results[0]['content'] == 'test content'
        assert results[0]['metadata']['url'] == 'test.com'
        assert results[0]['similarity_score'] == 0.9

    @patch('src.rag_validation.qdrant_client.QdrantClient')
    def test_get_point_method(self, mock_qdrant_client):
        """Test the get_point method"""
        # Mock retrieve results
        mock_retrieve_result = [
            Mock(id='point1', payload={'content': 'test content', 'metadata': {'url': 'test.com'}})
        ]

        mock_client_instance = Mock()
        mock_client_instance.retrieve.return_value = mock_retrieve_result
        mock_qdrant_client.return_value = mock_client_instance

        # Set up environment
        os.environ['QDRANT_HOST'] = 'test-host'
        os.environ['QDRANT_API_KEY'] = 'test-key'
        os.environ['QDRANT_COLLECTION_NAME'] = 'test-collection'

        # Reload config
        import importlib
        importlib.reload(config)

        # Initialize client
        client_wrapper = QdrantClientWrapper()

        # Test get_point
        result = client_wrapper.get_point('point1')

        # Assertions
        assert result['id'] == 'point1'
        assert result['content'] == 'test content'
        assert result['metadata']['url'] == 'test.com'