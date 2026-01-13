import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from src.rag_validation.query_validator import QueryValidator
from src.rag_validation.entities import Query, TextChunk


class TestQueryValidator:
    """Unit tests for QueryValidator"""

    def setup_method(self):
        """Set up test fixtures before each test method"""
        # Set up environment variables
        os.environ['COHERE_API_KEY'] = 'test-cohere-key'
        os.environ['QDRANT_HOST'] = 'test-host'
        os.environ['QDRANT_API_KEY'] = 'test-key'
        os.environ['QDRANT_COLLECTION_NAME'] = 'test-collection'

    @patch('src.rag_validation.query_validator.CohereEmbedder')
    @patch('src.rag_validation.qdrant_client.QdrantClient')
    def test_validate_single_query(self, mock_qdrant_client, mock_cohere_embedder):
        """Test validating a single query"""
        # Mock Cohere embedder
        mock_embedder_instance = Mock()
        mock_embedder_instance.embed_query.return_value = [0.1, 0.2, 0.3]
        mock_cohere_embedder.return_value = mock_embedder_instance

        # Mock Qdrant client
        mock_qdrant_instance = Mock()
        mock_qdrant_instance.search.return_value = [
            {
                'id': 'chunk1',
                'content': 'test content',
                'metadata': {'url': 'test.com', 'title': 'Test'},
                'similarity_score': 0.9
            }
        ]
        from src.rag_validation.qdrant_client import QdrantClientWrapper
        QdrantClientWrapper.client = mock_qdrant_instance

        # Create validator and test
        validator = QueryValidator()
        result = validator.validate_single_query("test query", top_k=1)

        # Verify results
        assert result.query_id.startswith('query-')
        assert len(result.retrieved_chunks) == 1
        assert result.retrieved_chunks[0].content == 'test content'
        assert result.similarity_scores[0] == 0.9
        assert result.top_k == 1

    @patch('src.rag_validation.query_validator.CohereEmbedder')
    @patch('src.rag_validation.qdrant_client.QdrantClient')
    def test_validate_batch_queries(self, mock_qdrant_client, mock_cohere_embedder):
        """Test validating multiple queries"""
        # Mock Cohere embedder
        mock_embedder_instance = Mock()
        mock_embedder_instance.embed_query.return_value = [0.1, 0.2, 0.3]
        mock_cohere_embedder.return_value = mock_embedder_instance

        # Mock Qdrant client
        mock_qdrant_instance = Mock()
        mock_qdrant_instance.search.return_value = [
            {
                'id': 'chunk1',
                'content': 'test content',
                'metadata': {'url': 'test.com', 'title': 'Test'},
                'similarity_score': 0.9
            }
        ]
        from src.rag_validation.qdrant_client import QdrantClientWrapper
        QdrantClientWrapper.client = mock_qdrant_instance

        # Create validator and test
        validator = QueryValidator()
        results = validator.validate_batch_queries(["query 1", "query 2"], top_k=1)

        # Verify results
        assert len(results) == 2
        assert all(len(result.retrieved_chunks) == 1 for result in results)

    @patch('src.rag_validation.query_validator.CohereEmbedder')
    @patch('src.rag_validation.qdrant_client.QdrantClient')
    def test_execute_semantic_search(self, mock_qdrant_client, mock_cohere_embedder):
        """Test executing semantic search"""
        # Mock Cohere embedder
        mock_embedder_instance = Mock()
        mock_embedder_instance.embed_query.return_value = [0.1, 0.2, 0.3]
        mock_cohere_embedder.return_value = mock_embedder_instance

        # Mock Qdrant client
        mock_qdrant_instance = Mock()
        mock_qdrant_instance.search.return_value = [
            {
                'id': 'chunk1',
                'content': 'test content',
                'metadata': {'url': 'test.com', 'title': 'Test'},
                'similarity_score': 0.9
            }
        ]
        from src.rag_validation.qdrant_client import QdrantClientWrapper
        QdrantClientWrapper.client = mock_qdrant_instance

        # Create validator and test
        validator = QueryValidator()
        result = validator.execute_semantic_search("test query", top_k=1)

        # Verify results
        assert result['original_query'] == 'test query'
        assert len(result['retrieved_chunks']) == 1
        assert result['retrieved_chunks'][0]['content'] == 'test content'
        assert result['retrieved_chunks'][0]['similarity_score'] == 0.9
        assert result['top_k'] == 1

    @patch('src.rag_validation.query_validator.CohereEmbedder')
    @patch('src.rag_validation.qdrant_client.QdrantClient')
    def test_validate_top_k_retrieval(self, mock_qdrant_client, mock_cohere_embedder):
        """Test top-k retrieval functionality"""
        # Mock Cohere embedder
        mock_embedder_instance = Mock()
        mock_embedder_instance.embed_query.return_value = [0.1, 0.2, 0.3]
        mock_cohere_embedder.return_value = mock_embedder_instance

        # Mock Qdrant client
        mock_qdrant_instance = Mock()
        mock_qdrant_instance.search.return_value = [
            {
                'id': 'chunk1',
                'content': 'test content 1',
                'metadata': {'url': 'test1.com', 'title': 'Test1'},
                'similarity_score': 0.9
            },
            {
                'id': 'chunk2',
                'content': 'test content 2',
                'metadata': {'url': 'test2.com', 'title': 'Test2'},
                'similarity_score': 0.8
            }
        ]
        from src.rag_validation.qdrant_client import QdrantClientWrapper
        QdrantClientWrapper.client = mock_qdrant_instance

        # Create validator and test
        validator = QueryValidator()
        result = validator.validate_top_k_retrieval("test query", top_k=2)

        # Verify results
        assert len(result.retrieved_chunks) == 2
        assert result.top_k == 2

    def test_categorize_query_method(self):
        """Test the query categorization method"""
        validator = QueryValidator()

        # Test ROS2 category
        assert validator._categorize_query("What is ROS2?") == 'ROS2'
        assert validator._categorize_query("Explain ROS2 nodes") == 'ROS2'

        # Test Gazebo category
        assert validator._categorize_query("How to use Gazebo?") == 'Gazebo'
        assert validator._categorize_query("Gazebo simulation") == 'Gazebo'

        # Test Isaac category
        assert validator._categorize_query("Isaac Sim tutorial") == 'Isaac'
        assert validator._categorize_query("How to use Isaac?") == 'Isaac'

        # Test VLA category
        assert validator._categorize_query("VLA models explained") == 'VLA'
        assert validator._categorize_query("Vision Language Action") == 'VLA'

        # Test General category
        assert validator._categorize_query("What is machine learning?") == 'General'
        assert validator._categorize_query("Random question") == 'General'

    @patch('src.rag_validation.query_validator.CohereEmbedder')
    @patch('src.rag_validation.qdrant_client.QdrantClient')
    def test_integrate_cohere_with_qdrant(self, mock_qdrant_client, mock_cohere_embedder):
        """Test integration between Cohere and Qdrant"""
        # Mock Cohere embedder
        mock_embedder_instance = Mock()
        mock_embedder_instance.embed_query.return_value = [0.1, 0.2, 0.3]
        mock_cohere_embedder.return_value = mock_embedder_instance

        # Mock Qdrant client
        mock_qdrant_instance = Mock()
        mock_qdrant_instance.search.return_value = [
            {
                'id': 'chunk1',
                'content': 'test content',
                'metadata': {'url': 'test.com', 'title': 'Test'},
                'similarity_score': 0.9
            }
        ]
        from src.rag_validation.qdrant_client import QdrantClientWrapper
        QdrantClientWrapper.client = mock_qdrant_instance

        # Create validator and test
        validator = QueryValidator()
        result = validator.integrate_cohere_with_qdrant("test query", top_k=1)

        # Verify results
        assert len(result.retrieved_chunks) == 1
        assert result.similarity_scores[0] == 0.9