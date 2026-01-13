import pytest
import os
from unittest.mock import Mock, patch
from src.rag_validation.result_evaluator import ResultEvaluator
from src.rag_validation.entities import QueryResult, TextChunk


class TestResultEvaluator:
    """Unit tests for ResultEvaluator"""

    def setup_method(self):
        """Set up test fixtures before each test method"""
        # Set up environment variables
        os.environ['VALIDATION_THRESHOLD'] = '0.7'

    def test_evaluate_query_result(self):
        """Test evaluating a single query result"""
        evaluator = ResultEvaluator()

        # Create a sample QueryResult
        chunk1 = TextChunk(
            id="chunk1",
            content="Test content 1",
            metadata={'url': 'test.com', 'page_title': 'Test', 'section': 'Section 1'}
        )
        chunk2 = TextChunk(
            id="chunk2",
            content="Test content 2",
            metadata={'url': 'test2.com', 'page_title': 'Test2', 'section': 'Section 2'}
        )

        query_result = QueryResult(
            query_id="test-query-1",
            retrieved_chunks=[chunk1, chunk2],
            similarity_scores=[0.9, 0.8],
            retrieval_time_ms=100.0,
            top_k=2
        )

        # Evaluate the result
        validation_result = evaluator.evaluate_query_result(query_result)

        # Verify the validation result
        assert validation_result.query_result_id == "test-query-1"
        assert validation_result.precision_at_k > 0
        assert validation_result.recall_at_k > 0
        assert validation_result.relevance_score > 0
        assert validation_result.semantic_alignment > 0
        assert validation_result.metadata_accuracy is True

    def test_calculate_precision_at_k(self):
        """Test calculating precision at k"""
        evaluator = ResultEvaluator()

        # Test with high scores (all should be relevant)
        scores_high = [0.9, 0.8, 0.75]
        precision = evaluator._calculate_precision_at_k(scores_high)
        assert precision == 1.0  # All scores above default threshold of 0.7

        # Test with mixed scores
        scores_mixed = [0.9, 0.6, 0.5]
        precision = evaluator._calculate_precision_at_k(scores_mixed)
        assert precision == 1/3  # Only 1 out of 3 above threshold

        # Test with empty scores
        precision = evaluator._calculate_precision_at_k([])
        assert precision == 0.0

    def test_calculate_relevance_score(self):
        """Test calculating relevance score"""
        evaluator = ResultEvaluator()

        # Test with scores
        scores = [0.9, 0.8, 0.7]
        relevance = evaluator._calculate_relevance_score(scores)
        expected = sum(scores) / len(scores)
        assert relevance == expected

        # Test with empty scores
        relevance = evaluator._calculate_relevance_score([])
        assert relevance == 0.0

    def test_validate_metadata_accuracy(self):
        """Test validating metadata accuracy"""
        evaluator = ResultEvaluator()

        # Test with valid metadata
        chunk_with_metadata = TextChunk(
            id="chunk1",
            content="Test content",
            metadata={'url': 'test.com', 'page_title': 'Test', 'section': 'Section 1'}
        )
        result = evaluator._validate_metadata_accuracy([chunk_with_metadata])
        assert result is True

        # Test with missing metadata
        chunk_no_metadata = TextChunk(
            id="chunk2",
            content="Test content",
            metadata={}
        )
        result = evaluator._validate_metadata_accuracy([chunk_no_metadata])
        assert result is False

        # Test with missing required field
        chunk_missing_field = TextChunk(
            id="chunk3",
            content="Test content",
            metadata={'url': 'test.com', 'page_title': 'Test'}  # Missing 'section'
        )
        result = evaluator._validate_metadata_accuracy([chunk_missing_field])
        assert result is False

        # Test with empty list
        result = evaluator._validate_metadata_accuracy([])
        assert result is True

    def test_calculate_validation_metrics(self):
        """Test calculating validation metrics for multiple results"""
        evaluator = ResultEvaluator()

        # Create sample query results
        chunk1 = TextChunk(
            id="chunk1",
            content="Test content 1",
            metadata={'url': 'test.com', 'page_title': 'Test', 'section': 'Section 1'}
        )
        chunk2 = TextChunk(
            id="chunk2",
            content="Test content 2",
            metadata={'url': 'test2.com', 'page_title': 'Test2', 'section': 'Section 2'}
        )

        query_result1 = QueryResult(
            query_id="test-query-1",
            retrieved_chunks=[chunk1],
            similarity_scores=[0.9],
            retrieval_time_ms=100.0,
            top_k=1
        )

        query_result2 = QueryResult(
            query_id="test-query-2",
            retrieved_chunks=[chunk2],
            similarity_scores=[0.8],
            retrieval_time_ms=150.0,
            top_k=1
        )

        results = [query_result1, query_result2]

        # Calculate metrics
        metrics = evaluator.calculate_validation_metrics(results)

        # Verify metrics exist
        assert "avg_query_time_ms" in metrics
        assert "avg_semantic_alignment" in metrics
        assert "metadata_accuracy_rate" in metrics
        assert "pipeline_stability" in metrics

        # Verify average query time
        assert metrics["avg_query_time_ms"] == 125.0  # (100 + 150) / 2

    def test_validate_metadata_accuracy_method(self):
        """Test the validate_metadata_accuracy method (T028)"""
        evaluator = ResultEvaluator()

        # Create chunks with valid metadata
        chunk_with_valid_metadata = TextChunk(
            id="chunk1",
            content="Test content",
            metadata={'url': 'test.com', 'page_title': 'Test', 'section': 'Section 1'}
        )

        result = evaluator.validate_metadata_accuracy([chunk_with_valid_metadata])
        assert result is True

    def test_evaluate_semantic_alignment_method(self):
        """Test the evaluate_semantic_alignment method (T029)"""
        evaluator = ResultEvaluator()

        # Test with similarity scores
        scores = [0.9, 0.8, 0.7]
        alignment = evaluator.evaluate_semantic_alignment(scores)
        expected = sum(scores) / len(scores)
        assert alignment == expected

    def test_implement_pipeline_stability_checks(self):
        """Test the implement_pipeline_stability_checks method (T031)"""
        evaluator = ResultEvaluator()

        # Create sample query results
        chunk1 = TextChunk(
            id="chunk1",
            content="Test content 1",
            metadata={'url': 'test.com', 'page_title': 'Test', 'section': 'Section 1'}
        )

        query_result1 = QueryResult(
            query_id="test-query-1",
            retrieved_chunks=[chunk1],
            similarity_scores=[0.9],
            retrieval_time_ms=100.0,
            top_k=1
        )

        query_result2 = QueryResult(
            query_id="test-query-2",
            retrieved_chunks=[chunk1],
            similarity_scores=[0.85],
            retrieval_time_ms=110.0,
            top_k=1
        )

        results = [query_result1, query_result2]

        # Test stability checks
        stability_result = evaluator.implement_pipeline_stability_checks(results)

        # Verify the result contains expected keys
        assert "avg_query_time_ms" in stability_result
        assert "avg_semantic_alignment" in stability_result
        assert "pipeline_stability" in stability_result

    def test_generate_validation_report(self):
        """Test generating validation report (T032)"""
        evaluator = ResultEvaluator()

        # Create sample query results
        chunk1 = TextChunk(
            id="chunk1",
            content="Test content 1",
            metadata={'url': 'test.com', 'page_title': 'Test', 'section': 'Section 1'}
        )
        chunk2 = TextChunk(
            id="chunk2",
            content="Test content 2",
            metadata={'url': 'test2.com', 'page_title': 'Test2', 'section': 'Section 2'}
        )

        query_result1 = QueryResult(
            query_id="test-query-1",
            retrieved_chunks=[chunk1],
            similarity_scores=[0.9],
            retrieval_time_ms=100.0,
            top_k=1
        )

        query_result2 = QueryResult(
            query_id="test-query-2",
            retrieved_chunks=[chunk2],
            similarity_scores=[0.8],
            retrieval_time_ms=150.0,
            top_k=1
        )

        results = [query_result1, query_result2]

        # Generate report
        report = evaluator.generate_validation_report(results)

        # Verify report structure
        assert "total_queries" in report
        assert "overall_metrics" in report
        assert "individual_results" in report
        assert "validation_summary" in report

        assert report["total_queries"] == 2
        assert len(report["individual_results"]) == 2

    def test_run_comprehensive_validation(self):
        """Test running comprehensive validation"""
        evaluator = ResultEvaluator()

        queries = ["What is ROS2?", "Explain Gazebo?"]

        # Since this method requires full validation pipeline,
        # we'll just test that it returns a structure with expected keys
        # (in a real test, we'd mock the dependencies)
        with patch('src.rag_validation.result_evaluator.QueryValidator') as mock_validator_class:
            # Mock the validator instance
            mock_validator = Mock()
            mock_chunk = TextChunk(
                id="chunk1",
                content="Test content",
                metadata={'url': 'test.com', 'page_title': 'Test', 'section': 'Section 1'}
            )
            mock_result = QueryResult(
                query_id="test-query",
                retrieved_chunks=[mock_chunk],
                similarity_scores=[0.9],
                retrieval_time_ms=100.0,
                top_k=1
            )
            mock_validator.validate_single_query.return_value = mock_result
            mock_validator_class.return_value = mock_validator

            # Run comprehensive validation
            report = evaluator.run_comprehensive_validation(queries, top_k=1)

            # Verify report structure
            assert "total_queries" in report
            assert "overall_metrics" in report
            assert "individual_results" in report
            assert "total_execution_time_ms" in report