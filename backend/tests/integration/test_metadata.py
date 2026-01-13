import pytest
import os
from unittest.mock import Mock, patch
from src.rag_validation.result_evaluator import ResultEvaluator
from src.rag_validation.entities import QueryResult, TextChunk


class TestMetadataIntegration:
    """Integration tests for metadata accuracy"""

    def setup_method(self):
        """Set up test fixtures before each test method"""
        # Set up environment variables
        os.environ['COHERE_API_KEY'] = 'test-cohere-key'
        os.environ['QDRANT_HOST'] = 'test-host'
        os.environ['QDRANT_API_KEY'] = 'test-key'
        os.environ['QDRANT_COLLECTION_NAME'] = 'test-collection'
        os.environ['VALIDATION_THRESHOLD'] = '0.7'

    @patch('src.rag_validation.query_validator.CohereEmbedder')
    @patch('src.rag_validation.qdrant_client.QdrantClient')
    def test_metadata_accuracy_with_real_evaluator(self, mock_qdrant_client, mock_cohere_embedder):
        """Test metadata accuracy validation with result evaluator"""
        # Mock Cohere embedder
        mock_embedder_instance = Mock()
        mock_embedder_instance.embed_query.return_value = [0.1, 0.2, 0.3]
        mock_cohere_embedder.return_value = mock_embedder_instance

        # Mock Qdrant client
        mock_qdrant_instance = Mock()
        mock_qdrant_instance.search.return_value = [
            {
                'id': 'chunk1',
                'content': 'ROS2 is a flexible framework for writing robot software',
                'metadata': {
                    'url': 'https://docs.ros.org/en/rolling/index.html',
                    'page_title': 'ROS 2 Documentation',
                    'section': 'Introduction',
                    'source_file': 'ros2_docs.md'
                },
                'similarity_score': 0.95
            }
        ]
        from src.rag_validation.qdrant_client import QdrantClientWrapper
        QdrantClientWrapper.client = mock_qdrant_instance

        # Import and use the query validator to generate a real result
        from src.rag_validation.query_validator import QueryValidator
        validator = QueryValidator()
        query_result = validator.validate_single_query("What is ROS2?", top_k=1)

        # Now evaluate the result for metadata accuracy
        evaluator = ResultEvaluator()
        validation_result = evaluator.evaluate_query_result(query_result)

        # Verify metadata accuracy is True (since our mock data has all required fields)
        assert validation_result.metadata_accuracy is True

    @patch('src.rag_validation.query_validator.CohereEmbedder')
    @patch('src.rag_validation.qdrant_client.QdrantClient')
    def test_metadata_inaccuracy_detection(self, mock_qdrant_client, mock_cohere_embedder):
        """Test detection of metadata inaccuracy"""
        # Mock Cohere embedder
        mock_embedder_instance = Mock()
        mock_embedder_instance.embed_query.return_value = [0.1, 0.2, 0.3]
        mock_cohere_embedder.return_value = mock_embedder_instance

        # Mock Qdrant client with incomplete metadata
        mock_qdrant_instance = Mock()
        mock_qdrant_instance.search.return_value = [
            {
                'id': 'chunk1',
                'content': 'Incomplete metadata test',
                'metadata': {
                    'url': 'https://example.com',
                    # Missing 'page_title' and 'section' - required fields
                },
                'similarity_score': 0.85
            }
        ]
        from src.rag_validation.qdrant_client import QdrantClientWrapper
        QdrantClientWrapper.client = mock_qdrant_instance

        # Import and use the query validator to generate a result with incomplete metadata
        from src.rag_validation.query_validator import QueryValidator
        validator = QueryValidator()
        query_result = validator.validate_single_query("Test query", top_k=1)

        # Now evaluate the result for metadata accuracy
        evaluator = ResultEvaluator()
        validation_result = evaluator.evaluate_query_result(query_result)

        # Verify metadata accuracy is False (since required fields are missing)
        assert validation_result.metadata_accuracy is False

    @patch('src.rag_validation.query_validator.CohereEmbedder')
    @patch('src.rag_validation.qdrant_client.QdrantClient')
    def test_complete_metadata_validation(self, mock_qdrant_client, mock_cohere_embedder):
        """Test complete metadata validation with multiple chunks"""
        # Mock Cohere embedder
        mock_embedder_instance = Mock()
        mock_embedder_instance.embed_query.return_value = [0.1, 0.2, 0.3]
        mock_cohere_embedder.return_value = mock_embedder_instance

        # Mock Qdrant client with multiple results, all with complete metadata
        mock_qdrant_instance = Mock()
        mock_qdrant_instance.search.return_value = [
            {
                'id': 'chunk1',
                'content': 'First result with complete metadata',
                'metadata': {
                    'url': 'https://example1.com',
                    'page_title': 'Example Page 1',
                    'section': 'Section A',
                    'source_file': 'doc1.md'
                },
                'similarity_score': 0.95
            },
            {
                'id': 'chunk2',
                'content': 'Second result with complete metadata',
                'metadata': {
                    'url': 'https://example2.com',
                    'page_title': 'Example Page 2',
                    'section': 'Section B',
                    'source_file': 'doc2.md'
                },
                'similarity_score': 0.88
            }
        ]
        from src.rag_validation.qdrant_client import QdrantClientWrapper
        QdrantClientWrapper.client = mock_qdrant_instance

        # Import and use the query validator
        from src.rag_validation.query_validator import QueryValidator
        validator = QueryValidator()
        query_result = validator.validate_single_query("Test query", top_k=2)

        # Evaluate the result
        evaluator = ResultEvaluator()
        validation_result = evaluator.evaluate_query_result(query_result)

        # Verify metadata accuracy is True (all chunks have complete metadata)
        assert validation_result.metadata_accuracy is True
        # Also verify we have the right number of chunks
        assert len(query_result.retrieved_chunks) == 2

    def test_metadata_accuracy_with_entity_objects(self):
        """Test metadata validation directly with entity objects"""
        evaluator = ResultEvaluator()

        # Create TextChunk entities directly with valid metadata
        valid_chunk = TextChunk(
            id="valid-chunk",
            content="Valid content with complete metadata",
            metadata={
                'url': 'https://valid-example.com',
                'page_title': 'Valid Page',
                'section': 'Valid Section'
            }
        )

        # Create QueryResult with valid metadata
        valid_query_result = QueryResult(
            query_id="valid-query",
            retrieved_chunks=[valid_chunk],
            similarity_scores=[0.9],
            retrieval_time_ms=100.0,
            top_k=1
        )

        # Evaluate
        validation_result = evaluator.evaluate_query_result(valid_query_result)
        assert validation_result.metadata_accuracy is True

        # Create TextChunk with missing metadata
        invalid_chunk = TextChunk(
            id="invalid-chunk",
            content="Invalid content with incomplete metadata",
            metadata={
                'url': 'https://invalid-example.com'
                # Missing 'page_title' and 'section'
            }
        )

        # Create QueryResult with invalid metadata
        invalid_query_result = QueryResult(
            query_id="invalid-query",
            retrieved_chunks=[invalid_chunk],
            similarity_scores=[0.8],
            retrieval_time_ms=120.0,
            top_k=1
        )

        # Evaluate
        validation_result = evaluator.evaluate_query_result(invalid_query_result)
        assert validation_result.metadata_accuracy is False

    @patch('src.rag_validation.query_validator.CohereEmbedder')
    @patch('src.rag_validation.qdrant_client.QdrantClient')
    def test_metadata_accuracy_validation_method(self, mock_qdrant_client, mock_cohere_embedder):
        """Test the specific metadata validation method (T028)"""
        # Mock Cohere embedder
        mock_embedder_instance = Mock()
        mock_embedder_instance.embed_query.return_value = [0.1, 0.2, 0.3]
        mock_cohere_embedder.return_value = mock_embedder_instance

        # Mock Qdrant client
        mock_qdrant_instance = Mock()
        mock_qdrant_instance.search.return_value = [
            {
                'id': 'chunk1',
                'content': 'Test content',
                'metadata': {
                    'url': 'https://example.com',
                    'page_title': 'Example Page',
                    'section': 'Example Section'
                },
                'similarity_score': 0.9
            }
        ]
        from src.rag_validation.qdrant_client import QdrantClientWrapper
        QdrantClientWrapper.client = mock_qdrant_instance

        # Import and use the query validator
        from src.rag_validation.query_validator import QueryValidator
        validator = QueryValidator()
        query_result = validator.validate_single_query("Test query", top_k=1)

        # Use the specific validation method
        evaluator = ResultEvaluator()
        is_accurate = evaluator.validate_metadata_accuracy(query_result.retrieved_chunks)

        # Verify result
        assert is_accurate is True

    @patch('src.rag_validation.query_validator.CohereEmbedder')
    @patch('src.rag_validation.qdrant_client.QdrantClient')
    def test_batch_metadata_accuracy_validation(self, mock_qdrant_client, mock_cohere_embedder):
        """Test metadata accuracy validation for batch results"""
        # Mock Cohere embedder
        mock_embedder_instance = Mock()
        mock_embedder_instance.embed_query.return_value = [0.1, 0.2, 0.3]
        mock_cohere_embedder.return_value = mock_embedder_instance

        # Mock Qdrant client with results that have mixed metadata quality
        mock_qdrant_instance = Mock()
        mock_qdrant_instance.search.return_value = [
            {
                'id': 'chunk1',
                'content': 'First result with complete metadata',
                'metadata': {
                    'url': 'https://example1.com',
                    'page_title': 'Example Page 1',
                    'section': 'Section A'
                },
                'similarity_score': 0.9
            },
            {
                'id': 'chunk2',
                'content': 'Second result with incomplete metadata',
                'metadata': {
                    'url': 'https://example2.com'
                    # Missing required fields
                },
                'similarity_score': 0.8
            }
        ]
        from src.rag_validation.qdrant_client import QdrantClientWrapper
        QdrantClientWrapper.client = mock_qdrant_instance

        # Import and use the query validator
        from src.rag_validation.query_validator import QueryValidator
        validator = QueryValidator()
        query_result = validator.validate_single_query("Test query", top_k=2)

        # Use the specific validation method
        evaluator = ResultEvaluator()
        is_accurate = evaluator.validate_metadata_accuracy(query_result.retrieved_chunks)

        # Since one chunk has incomplete metadata, the overall accuracy should be False
        assert is_accurate is False