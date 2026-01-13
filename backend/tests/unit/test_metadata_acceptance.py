import pytest
import os
from unittest.mock import Mock, patch
from src.rag_validation.result_evaluator import ResultEvaluator
from src.rag_validation.entities import QueryResult, TextChunk


class TestMetadataAcceptance:
    """Acceptance tests for metadata accuracy (T037)"""

    def setup_method(self):
        """Set up test fixtures before each test method"""
        # Set up environment variables
        os.environ['VALIDATION_THRESHOLD'] = '0.7'

    def test_metadata_accuracy_100_percent_requirement(self):
        """Test that metadata accuracy meets the acceptance criteria: 100% of chunks have accurate metadata"""
        evaluator = ResultEvaluator()

        # Create chunks with complete and valid metadata (all required fields present)
        valid_chunk1 = TextChunk(
            id="chunk1",
            content="Test content with complete metadata",
            metadata={
                'url': 'https://example1.com',
                'page_title': 'Example Page 1',
                'section': 'Section 1',
                'source_file': 'doc1.md'
            }
        )

        valid_chunk2 = TextChunk(
            id="chunk2",
            content="Another test content with complete metadata",
            metadata={
                'url': 'https://example2.com',
                'page_title': 'Example Page 2',
                'section': 'Section 2',
                'source_file': 'doc2.md'
            }
        )

        # Create a QueryResult with valid chunks
        query_result = QueryResult(
            query_id="test-query",
            retrieved_chunks=[valid_chunk1, valid_chunk2],
            similarity_scores=[0.9, 0.85],
            retrieval_time_ms=100.0,
            top_k=2
        )

        # Evaluate the result
        validation_result = evaluator.evaluate_query_result(query_result)

        # Verify that metadata accuracy is 100% (True)
        assert validation_result.metadata_accuracy is True

        # Also verify through the specific validation method
        is_accurate = evaluator.validate_metadata_accuracy([valid_chunk1, valid_chunk2])
        assert is_accurate is True

    def test_metadata_inaccuracy_detection(self):
        """Test detection when metadata is not 100% accurate"""
        evaluator = ResultEvaluator()

        # Create one chunk with complete metadata
        valid_chunk = TextChunk(
            id="valid-chunk",
            content="Valid content",
            metadata={
                'url': 'https://example.com',
                'page_title': 'Example Page',
                'section': 'Section 1'
            }
        )

        # Create one chunk with missing required metadata field
        invalid_chunk = TextChunk(
            id="invalid-chunk",
            content="Invalid content with missing metadata",
            metadata={
                'url': 'https://example2.com',
                'page_title': 'Example Page 2'
                # Missing 'section' field
            }
        )

        # Create a QueryResult with mixed quality metadata
        query_result = QueryResult(
            query_id="test-query",
            retrieved_chunks=[valid_chunk, invalid_chunk],
            similarity_scores=[0.9, 0.8],
            retrieval_time_ms=120.0,
            top_k=2
        )

        # Evaluate the result
        validation_result = evaluator.evaluate_query_result(query_result)

        # Since one chunk has incomplete metadata, overall accuracy should be False
        assert validation_result.metadata_accuracy is False

        # Also verify through the specific validation method
        is_accurate = evaluator.validate_metadata_accuracy([valid_chunk, invalid_chunk])
        assert is_accurate is False

    def test_empty_metadata_detection(self):
        """Test detection when metadata is completely empty"""
        evaluator = ResultEvaluator()

        # Create chunk with empty metadata
        empty_metadata_chunk = TextChunk(
            id="empty-chunk",
            content="Content with no metadata",
            metadata={}
        )

        # Create a QueryResult with empty metadata
        query_result = QueryResult(
            query_id="test-query",
            retrieved_chunks=[empty_metadata_chunk],
            similarity_scores=[0.7],
            retrieval_time_ms=80.0,
            top_k=1
        )

        # Evaluate the result
        validation_result = evaluator.evaluate_query_result(query_result)

        # Should be False since required fields are missing
        assert validation_result.metadata_accuracy is False

        # Verify through the specific validation method
        is_accurate = evaluator.validate_metadata_accuracy([empty_metadata_chunk])
        assert is_accurate is False

    def test_none_metadata_detection(self):
        """Test detection when metadata is None"""
        evaluator = ResultEvaluator()

        # Create chunk with None metadata
        none_metadata_chunk = TextChunk(
            id="none-chunk",
            content="Content with no metadata",
            metadata=None  # This will be converted to empty dict in __post_init__ but let's test direct assignment
        )
        # Manually set to None after creation to test the case
        none_metadata_chunk.metadata = None

        # Create a QueryResult with None metadata
        query_result = QueryResult(
            query_id="test-query",
            retrieved_chunks=[none_metadata_chunk],
            similarity_scores=[0.75],
            retrieval_time_ms=90.0,
            top_k=1
        )

        # Evaluate the result
        validation_result = evaluator.evaluate_query_result(query_result)

        # Should be False since required fields are missing
        assert validation_result.metadata_accuracy is False

    def test_all_required_fields_present(self):
        """Test that all required metadata fields must be present and non-empty"""
        evaluator = ResultEvaluator()

        # Test with all required fields present and non-empty
        complete_chunk = TextChunk(
            id="complete-chunk",
            content="Complete metadata test",
            metadata={
                'url': 'https://example.com',
                'page_title': 'Example Page',
                'section': 'Section 1'
            }
        )

        is_accurate = evaluator.validate_metadata_accuracy([complete_chunk])
        assert is_accurate is True

        # Test with all required fields but one empty
        incomplete_chunk = TextChunk(
            id="incomplete-chunk",
            content="Incomplete metadata test",
            metadata={
                'url': 'https://example.com',
                'page_title': 'Example Page',
                'section': ''  # Empty section
            }
        )

        is_accurate = evaluator.validate_metadata_accuracy([incomplete_chunk])
        assert is_accurate is False

        # Test with missing required field
        missing_chunk = TextChunk(
            id="missing-chunk",
            content="Missing field test",
            metadata={
                'url': 'https://example.com',
                'page_title': 'Example Page'
                # Missing 'section' field
            }
        )

        is_accurate = evaluator.validate_metadata_accuracy([missing_chunk])
        assert is_accurate is False

    @patch('src.rag_validation.query_validator.CohereEmbedder')
    @patch('src.rag_validation.qdrant_client.QdrantClient')
    def test_metadata_acceptance_with_simulated_validation(self, mock_qdrant_client, mock_cohere_embedder):
        """Test metadata acceptance in the context of a full validation flow"""
        # Mock Cohere embedder
        mock_embedder_instance = Mock()
        mock_embedder_instance.embed_query.return_value = [0.1, 0.2, 0.3]
        mock_cohere_embedder.return_value = mock_embedder_instance

        # Mock Qdrant client with results that have complete metadata
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
                'similarity_score': 0.9
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
                'similarity_score': 0.85
            }
        ]
        from src.rag_validation.qdrant_client import QdrantClientWrapper
        QdrantClientWrapper.client = mock_qdrant_instance

        # Import and use the validation components
        from src.rag_validation.query_validator import QueryValidator
        from src.rag_validation.result_evaluator import ResultEvaluator

        validator = QueryValidator()
        evaluator = ResultEvaluator()

        # Validate a query
        query_result = validator.validate_single_query("Test query for metadata validation", top_k=2)

        # Evaluate the result
        validation_result = evaluator.evaluate_query_result(query_result)

        # Since all chunks in our mock have complete metadata, accuracy should be 100%
        assert validation_result.metadata_accuracy is True

        # Also test the metrics calculation which includes metadata accuracy
        metrics = evaluator.calculate_validation_metrics([query_result])
        assert metrics["metadata_accuracy_rate"] == 1.0  # 100% accuracy

    def test_metadata_acceptance_edge_cases(self):
        """Test edge cases for metadata acceptance"""
        evaluator = ResultEvaluator()

        # Test with whitespace-only values
        whitespace_chunk = TextChunk(
            id="whitespace-chunk",
            content="Whitespace test",
            metadata={
                'url': '   ',  # Whitespace only
                'page_title': 'Example Page',
                'section': 'Section 1'
            }
        )

        # The validation logic treats empty strings as missing values
        is_accurate = evaluator.validate_metadata_accuracy([whitespace_chunk])
        # This depends on the implementation - if the validation checks for truthiness,
        # whitespace-only strings might pass. Let's check the implementation logic.
        # In our implementation, we check `if field not in chunk.metadata or not chunk.metadata[field]`
        # So empty strings, whitespace-only strings would be considered "not" truthy.
        assert is_accurate is False

        # Test with empty string values
        empty_string_chunk = TextChunk(
            id="empty-string-chunk",
            content="Empty string test",
            metadata={
                'url': '',  # Empty string
                'page_title': 'Example Page',
                'section': 'Section 1'
            }
        )

        is_accurate = evaluator.validate_metadata_accuracy([empty_string_chunk])
        assert is_accurate is False

        # Test with valid values containing spaces
        valid_with_spaces = TextChunk(
            id="valid-spaces-chunk",
            content="Valid spaces test",
            metadata={
                'url': 'https://example.com/path with spaces',
                'page_title': 'Example Page with Spaces',
                'section': 'Section with Spaces'
            }
        )

        is_accurate = evaluator.validate_metadata_accuracy([valid_with_spaces])
        assert is_accurate is True