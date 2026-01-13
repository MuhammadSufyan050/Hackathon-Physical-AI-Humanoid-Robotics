import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from src.rag_validation.cohere_embedder import CohereEmbedder
from src.config.settings import config


class TestCohereEmbedder:
    """Unit tests for CohereEmbedder"""

    def setup_method(self):
        """Set up test fixtures before each test method"""
        # Set up environment variables
        os.environ['COHERE_API_KEY'] = 'test-cohere-key'
        os.environ['COHERE_MODEL'] = 'embed-english-v3.0'

    @patch('src.rag_validation.cohere_embedder.cohere.Client')
    def test_initialize_cohere_client(self, mock_cohere_client):
        """Test initializing Cohere client with API key"""
        # Mock the Cohere client
        mock_client_instance = Mock()
        mock_cohere_client.return_value = mock_client_instance

        # Create embedder instance
        embedder = CohereEmbedder()

        # Verify Cohere client was initialized with API key
        mock_cohere_client.assert_called_once_with('test-cohere-key')

    def test_initialize_without_api_key_raises_error(self):
        """Test that initializing without API key raises ValueError"""
        # Temporarily remove API key
        original_key = os.environ.get('COHERE_API_KEY')
        if 'COHERE_API_KEY' in os.environ:
            del os.environ['COHERE_API_KEY']

        try:
            with pytest.raises(ValueError, match="COHERE_API_KEY environment variable must be set"):
                CohereEmbedder()
        finally:
            # Restore original key
            if original_key:
                os.environ['COHERE_API_KEY'] = original_key

    @patch('src.rag_validation.cohere_embedder.cohere.Client')
    def test_embed_text_single(self, mock_cohere_client):
        """Test embedding a single text"""
        # Mock the Cohere client and response
        mock_client_instance = Mock()
        mock_response = Mock()
        mock_response.embeddings = [[0.1, 0.2, 0.3]]  # Mock embedding result
        mock_client_instance.embed.return_value = mock_response
        mock_cohere_client.return_value = mock_client_instance

        # Create embedder and test
        embedder = CohereEmbedder()
        result = embedder.embed_text("test query")

        # Verify the call was made correctly
        mock_client_instance.embed.assert_called_once_with(
            texts=["test query"],
            model="embed-english-v3.0",
            input_type="search_query"
        )

        # Verify the result
        assert result == [0.1, 0.2, 0.3]

    @patch('src.rag_validation.cohere_embedder.cohere.Client')
    def test_embed_texts_multiple(self, mock_cohere_client):
        """Test embedding multiple texts"""
        # Mock the Cohere client and response
        mock_client_instance = Mock()
        mock_response = Mock()
        mock_response.embeddings = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]  # Mock embeddings
        mock_client_instance.embed.return_value = mock_response
        mock_cohere_client.return_value = mock_client_instance

        # Create embedder and test
        embedder = CohereEmbedder()
        result = embedder.embed_texts(["test query 1", "test query 2"])

        # Verify the call was made correctly
        mock_client_instance.embed.assert_called_once_with(
            texts=["test query 1", "test query 2"],
            model="embed-english-v3.0",
            input_type="search_document"
        )

        # Verify the result
        assert result == [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]

    @patch('src.rag_validation.cohere_embedder.cohere.Client')
    def test_embed_query_alias(self, mock_cohere_client):
        """Test that embed_query is an alias for embed_text"""
        # Mock the Cohere client and response
        mock_client_instance = Mock()
        mock_response = Mock()
        mock_response.embeddings = [[0.1, 0.2, 0.3]]
        mock_client_instance.embed.return_value = mock_response
        mock_cohere_client.return_value = mock_client_instance

        # Create embedder and test
        embedder = CohereEmbedder()
        result = embedder.embed_query("test query")

        # Verify the result is the same as embed_text
        assert result == [0.1, 0.2, 0.3]

    @patch('src.rag_validation.cohere_embedder.cohere.Client')
    def test_get_model_info(self, mock_cohere_client):
        """Test getting model information"""
        # Mock the Cohere client
        mock_client_instance = Mock()
        mock_cohere_client.return_value = mock_client_instance

        # Create embedder and test
        embedder = CohereEmbedder()
        info = embedder.get_model_info()

        # Verify the info
        assert info == {
            "model": "embed-english-v3.0",
            "api_key_set": True
        }

    @patch('src.rag_validation.cohere_embedder.cohere.Client')
    def test_embed_text_error_handling(self, mock_cohere_client):
        """Test error handling in embed_text method"""
        # Mock the Cohere client to raise an exception
        mock_client_instance = Mock()
        mock_client_instance.embed.side_effect = Exception("API Error")
        mock_cohere_client.return_value = mock_client_instance

        # Create embedder and test
        embedder = CohereEmbedder()

        with pytest.raises(Exception, match="API Error"):
            embedder.embed_text("test query")