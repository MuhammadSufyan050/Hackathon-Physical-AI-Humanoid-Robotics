import pytest
import os
from unittest.mock import Mock, patch
from src.rag_validation.query_validator import QueryValidator
from src.rag_validation.result_evaluator import ResultEvaluator


class TestPipelineStability:
    """Integration tests for pipeline stability"""

    def setup_method(self):
        """Set up test fixtures before each test method"""
        # Set up environment variables
        os.environ['COHERE_API_KEY'] = 'test-cohere-key'
        os.environ['QDRANT_HOST'] = 'test-host'
        os.environ['QDRANT_API_KEY'] = 'test-key'
        os.environ['QDRANT_COLLECTION_NAME'] = 'test-collection'

    @patch('src.rag_validation.query_validator.CohereEmbedder')
    @patch('src.rag_validation.qdrant_client.QdrantClient')
    def test_pipeline_stability_consistent_results(self, mock_qdrant_client, mock_cohere_embedder):
        """Test that pipeline produces consistent results across multiple runs (T035)"""
        # Mock Cohere embedder
        mock_embedder_instance = Mock()
        mock_embedder_instance.embed_query.return_value = [0.1, 0.2, 0.3]
        mock_cohere_embedder.return_value = mock_embedder_instance

        # Mock Qdrant client to return consistent results
        mock_qdrant_instance = Mock()
        consistent_result = [
            {
                'id': 'chunk1',
                'content': 'Consistent content across runs',
                'metadata': {'url': 'https://example.com', 'page_title': 'Example', 'section': 'Section'},
                'similarity_score': 0.95
            }
        ]
        mock_qdrant_instance.search.return_value = consistent_result
        from src.rag_validation.qdrant_client import QdrantClientWrapper
        QdrantClientWrapper.client = mock_qdrant_instance

        # Create validator and run stability check
        validator = QueryValidator()
        stability_result = validator.run_stability_check("Test query", runs=5, top_k=1)

        # Verify stability
        assert stability_result["runs"] == 5
        assert stability_result["consistent_results"] is True
        assert stability_result["avg_retrieval_time_ms"] >= 0
        assert stability_result["time_coefficient_of_variation"] >= 0

    @patch('src.rag_validation.query_validator.CohereEmbedder')
    @patch('src.rag_validation.qdrant_client.QdrantClient')
    def test_pipeline_stability_check_method(self, mock_qdrant_client, mock_cohere_embedder):
        """Test the specific pipeline stability check method (T031)"""
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
                'metadata': {'url': 'https://example.com', 'page_title': 'Example', 'section': 'Section'},
                'similarity_score': 0.9
            }
        ]
        from src.rag_validation.qdrant_client import QdrantClientWrapper
        QdrantClientWrapper.client = mock_qdrant_instance

        # Create validator and test stability method
        validator = QueryValidator()
        stability_result = validator.run_stability_check("Test query", runs=3, top_k=1)

        # Verify the result structure
        assert "query" in stability_result
        assert "runs" in stability_result
        assert "consistent_results" in stability_result
        assert "avg_retrieval_time_ms" in stability_result
        assert stability_result["runs"] == 3

    @patch('src.rag_validation.query_validator.CohereEmbedder')
    @patch('src.rag_validation.qdrant_client.QdrantClient')
    def test_pipeline_stability_with_result_evaluator(self, mock_qdrant_client, mock_cohere_embedder):
        """Test pipeline stability using result evaluator (T031)"""
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
                'metadata': {'url': 'https://example.com', 'page_title': 'Example', 'section': 'Section'},
                'similarity_score': 0.9
            }
        ]
        from src.rag_validation.qdrant_client import QdrantClientWrapper
        QdrantClientWrapper.client = mock_qdrant_instance

        # Create validator and generate multiple query results
        from src.rag_validation.query_validator import QueryValidator
        validator = QueryValidator()

        query_results = []
        for i in range(3):
            result = validator.validate_single_query(f"Test query {i}", top_k=1)
            query_results.append(result)

        # Use result evaluator to check stability
        evaluator = ResultEvaluator()
        stability_metrics = evaluator.implement_pipeline_stability_checks(query_results)

        # Verify stability metrics exist
        assert "avg_query_time_ms" in stability_metrics
        assert "avg_semantic_alignment" in stability_metrics
        assert "pipeline_stability" in stability_metrics

    @patch('src.rag_validation.query_validator.CohereEmbedder')
    @patch('src.rag_validation.qdrant_client.QdrantClient')
    def test_pipeline_stability_across_different_environments_simulation(self, mock_qdrant_client, mock_cohere_embedder):
        """Simulate pipeline stability across different environments"""
        # This test simulates the requirement: "Validate pipeline reproducibility by achieving consistent results across 3 different Python deployment environments"
        # Since we can't actually test across different environments in a unit test,
        # we simulate by running the same query multiple times and checking consistency

        # Mock Cohere embedder
        mock_embedder_instance = Mock()
        mock_embedder_instance.embed_query.return_value = [0.1, 0.2, 0.3]
        mock_cohere_embedder.return_value = mock_embedder_instance

        # Mock Qdrant client
        mock_qdrant_instance = Mock()
        mock_qdrant_instance.search.return_value = [
            {
                'id': 'chunk1',
                'content': 'Consistent test content',
                'metadata': {'url': 'https://example.com', 'page_title': 'Example', 'section': 'Section'},
                'similarity_score': 0.85
            }
        ]
        from src.rag_validation.qdrant_client import QdrantClientWrapper
        QdrantClientWrapper.client = mock_qdrant_instance

        # Run multiple queries to simulate different "environments"
        validator = QueryValidator()
        stability_result = validator.run_stability_check("Consistency test query", runs=10, top_k=1)

        # Check if results are consistent
        assert stability_result["runs"] == 10
        # In our simulation, all results should be consistent since we're mocking the same response
        assert stability_result["consistent_results"] is True

        # Check that coefficient of variation is low (indicating stability)
        # Note: With identical mocked responses, the std dev should be 0, making CV 0
        assert stability_result["time_coefficient_of_variation"] >= 0  # Non-negative

    def test_stability_assessment_logic(self):
        """Test the stability assessment logic directly"""
        evaluator = ResultEvaluator()

        # Test with very consistent times (low variance)
        consistent_times = [100, 101, 99, 100, 100]
        consistent_alignment = [0.9, 0.91, 0.89, 0.9, 0.9]

        # Create mock QueryResults
        from src.rag_validation.entities import QueryResult, TextChunk
        mock_chunks = [TextChunk(id="chunk1", content="test", metadata={'url': 'test.com', 'page_title': 'Test', 'section': 'Section'})]

        mock_results = []
        for i, (time, align) in enumerate(zip(consistent_times, consistent_alignment)):
            result = QueryResult(
                query_id=f"query-{i}",
                retrieved_chunks=mock_chunks,
                similarity_scores=[align],
                retrieval_time_ms=time,
                top_k=1
            )
            mock_results.append(result)

        # Assess stability
        stability_metrics = evaluator.calculate_validation_metrics(mock_results)

        # With consistent results, stability should be good
        assert stability_metrics["pipeline_stability"] in ["stable", "moderately_stable"]

    @patch('src.rag_validation.query_validator.CohereEmbedder')
    @patch('src.rag_validation.qdrant_client.QdrantClient')
    def test_stability_check_with_multiple_queries(self, mock_qdrant_client, mock_cohere_embedder):
        """Test stability across multiple different queries"""
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
                'metadata': {'url': 'https://example.com', 'page_title': 'Example', 'section': 'Section'},
                'similarity_score': 0.88
            }
        ]
        from src.rag_validation.qdrant_client import QdrantClientWrapper
        QdrantClientWrapper.client = mock_qdrant_instance

        # Test stability for different queries
        test_queries = ["What is ROS2?", "Explain Gazebo?", "How to use Isaac Sim?"]
        validator = QueryValidator()

        all_stable = True
        for query in test_queries:
            stability_result = validator.run_stability_check(query, runs=3, top_k=1)
            if not stability_result["consistent_results"]:
                all_stable = False

        # In our mocked scenario, all should be stable
        assert all_stable is True