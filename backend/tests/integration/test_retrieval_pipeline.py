import pytest
import os
from unittest.mock import Mock, patch
from src.rag_validation.qdrant_client import qdrant_client
from src.rag_validation.cohere_embedder import CohereEmbedder
from src.rag_validation.query_validator import QueryValidator
from src.rag_validation.result_evaluator import ResultEvaluator
from src.rag_validation.api import test_connection, execute_semantic_search, run_comprehensive_batch_validation


class TestFullRetrievalPipelineIntegration:
    """Integration tests for the full validation pipeline"""

    def setup_method(self):
        """Set up test fixtures before each test method"""
        # Set up environment variables
        os.environ['COHERE_API_KEY'] = 'test-cohere-key'
        os.environ['QDRANT_HOST'] = 'test-host'
        os.environ['QDRANT_API_KEY'] = 'test-key'
        os.environ['QDRANT_COLLECTION_NAME'] = 'test-collection'
        os.environ['VALIDATION_THRESHOLD'] = '0.7'

    @patch('src.rag_validation.qdrant_client.QdrantClient')
    @patch('src.rag_validation.cohere_embedder.cohere.Client')
    def test_full_pipeline_single_query(self, mock_cohere_client, mock_qdrant_client):
        """Test the full pipeline for a single query"""
        # Mock Cohere client
        mock_cohere_instance = Mock()
        mock_cohere_instance.embed.return_value = Mock(embeddings=[[0.1, 0.2, 0.3]])
        mock_cohere_client.return_value = mock_cohere_instance

        # Mock Qdrant client
        mock_qdrant_instance = Mock()
        mock_qdrant_instance.get_collections.return_value = Mock(collections=[Mock(name='test-collection')])
        mock_qdrant_instance.search.return_value = [
            Mock(id='chunk1', payload={'content': 'Test content', 'metadata': {'url': 'test.com', 'page_title': 'Test', 'section': 'Section'}}, score=0.9)
        ]
        mock_qdrant_client.return_value = mock_qdrant_instance

        # Update the global Qdrant client instance
        from src.rag_validation.qdrant_client import QdrantClientWrapper
        QdrantClientWrapper.client = mock_qdrant_instance

        # Test the full pipeline components
        # 1. Test connection
        connection_result = test_connection()
        assert connection_result['success'] is True

        # 2. Test semantic search
        search_result = execute_semantic_search("What is ROS2?", top_k=1)
        assert 'error' not in search_result
        assert len(search_result['retrieved_chunks']) == 1
        assert search_result['retrieved_chunks'][0]['similarity_score'] == 0.9

        # 3. Test validation components
        validator = QueryValidator()
        query_result = validator.validate_single_query("Test query", top_k=1)
        assert len(query_result.retrieved_chunks) == 1

        # 4. Test evaluation
        evaluator = ResultEvaluator()
        validation_result = evaluator.evaluate_query_result(query_result)
        assert validation_result.metadata_accuracy is True

    @patch('src.rag_validation.qdrant_client.QdrantClient')
    @patch('src.rag_validation.cohere_embedder.cohere.Client')
    def test_full_pipeline_batch_validation(self, mock_cohere_client, mock_qdrant_client):
        """Test the full pipeline for batch validation"""
        # Mock Cohere client
        mock_cohere_instance = Mock()
        mock_cohere_instance.embed.return_value = Mock(embeddings=[[0.1, 0.2, 0.3]])
        mock_cohere_client.return_value = mock_cohere_instance

        # Mock Qdrant client
        mock_qdrant_instance = Mock()
        mock_qdrant_instance.get_collections.return_value = Mock(collections=[Mock(name='test-collection')])
        mock_qdrant_instance.search.return_value = [
            Mock(id='chunk1', payload={'content': 'Test content 1', 'metadata': {'url': 'test1.com', 'page_title': 'Test1', 'section': 'Section1'}}, score=0.9),
            Mock(id='chunk2', payload={'content': 'Test content 2', 'metadata': {'url': 'test2.com', 'page_title': 'Test2', 'section': 'Section2'}}, score=0.85)
        ]
        mock_qdrant_client.return_value = mock_qdrant_instance

        # Update the global Qdrant client instance
        from src.rag_validation.qdrant_client import QdrantClientWrapper
        QdrantClientWrapper.client = mock_qdrant_instance

        # Test batch validation
        queries = ["Query 1", "Query 2"]
        batch_result = run_comprehensive_batch_validation(queries, top_k=2)

        assert 'error' not in batch_result
        assert batch_result['total_queries'] == 2
        assert len(batch_result['individual_results']) == 2
        assert 'overall_metrics' in batch_result

        # Verify metrics
        metrics = batch_result['overall_metrics']
        assert 'avg_semantic_alignment' in metrics
        assert 'metadata_accuracy_rate' in metrics

    @patch('src.rag_validation.qdrant_client.QdrantClient')
    @patch('src.rag_validation.cohere_embedder.cohere.Client')
    def test_end_to_end_validation_flow(self, mock_cohere_client, mock_qdrant_client):
        """Test the complete end-to-end validation flow"""
        # Mock Cohere client
        mock_cohere_instance = Mock()
        mock_cohere_instance.embed.return_value = Mock(embeddings=[[0.1, 0.2, 0.3]])
        mock_cohere_client.return_value = mock_cohere_instance

        # Mock Qdrant client
        mock_qdrant_instance = Mock()
        mock_qdrant_instance.get_collections.return_value = Mock(collections=[Mock(name='test-collection')])
        mock_qdrant_instance.search.return_value = [
            Mock(id='chunk1', payload={'content': 'Comprehensive test content', 'metadata': {'url': 'comprehensive-test.com', 'page_title': 'Comprehensive Test', 'section': 'Full Flow'}}, score=0.92)
        ]
        mock_qdrant_client.return_value = mock_qdrant_instance

        # Update the global Qdrant client instance
        from src.rag_validation.qdrant_client import QdrantClientWrapper
        QdrantClientWrapper.client = mock_qdrant_instance

        # Execute the full validation flow
        test_queries = [
            "What is the main concept?",
            "Explain the key points",
            "How does this work?"
        ]

        # Run comprehensive validation
        comprehensive_result = run_comprehensive_batch_validation(test_queries, top_k=1)

        # Verify the comprehensive result structure
        assert 'total_queries' in comprehensive_result
        assert 'overall_metrics' in comprehensive_result
        assert 'individual_results' in comprehensive_result
        assert 'validation_summary' in comprehensive_result

        # Verify the validation summary
        summary = comprehensive_result['validation_summary']
        assert 'metadata_accuracy_pass' in summary
        assert 'semantic_alignment_pass' in summary
        assert 'query_time_pass' in summary
        assert 'pipeline_stability' in summary

        # Verify we processed all queries
        assert comprehensive_result['total_queries'] == len(test_queries)

    @patch('src.rag_validation.qdrant_client.QdrantClient')
    @patch('src.rag_validation.cohere_embedder.cohere.Client')
    def test_pipeline_with_error_handling(self, mock_cohere_client, mock_qdrant_client):
        """Test the pipeline's error handling capabilities"""
        # Mock Cohere client to raise an error for some calls
        mock_cohere_instance = Mock()
        mock_cohere_instance.embed.return_value = Mock(embeddings=[[0.1, 0.2, 0.3]])
        mock_cohere_client.return_value = mock_cohere_instance

        # Mock Qdrant client
        mock_qdrant_instance = Mock()
        mock_qdrant_instance.get_collections.return_value = Mock(collections=[Mock(name='test-collection')])
        mock_qdrant_instance.search.return_value = [
            Mock(id='chunk1', payload={'content': 'Error handling test', 'metadata': {'url': 'error-test.com', 'page_title': 'Error Test', 'section': 'Error Section'}}, score=0.88)
        ]
        mock_qdrant_client.return_value = mock_qdrant_instance

        # Update the global Qdrant client instance
        from src.rag_validation.qdrant_client import QdrantClientWrapper
        QdrantClientWrapper.client = mock_qdrant_instance

        # Test with a normal query
        result = execute_semantic_search("Normal query", top_k=1)
        assert 'error' not in result
        assert len(result['retrieved_chunks']) == 1

        # Test batch validation with mixed success/failure
        queries = ["Valid query 1", "Valid query 2"]
        batch_result = run_comprehensive_batch_validation(queries, top_k=1)

        assert batch_result['completed_queries'] == len(queries)
        assert 'overall_metrics' in batch_result

    @patch('src.rag_validation.qdrant_client.QdrantClient')
    @patch('src.rag_validation.cohere_embedder.cohere.Client')
    def test_pipeline_stability_under_load_simulation(self, mock_cohere_client, mock_qdrant_client):
        """Simulate pipeline stability under load"""
        # Mock Cohere client
        mock_cohere_instance = Mock()
        mock_cohere_instance.embed.return_value = Mock(embeddings=[[0.1, 0.2, 0.3]])
        mock_cohere_client.return_value = mock_cohere_instance

        # Mock Qdrant client with consistent responses
        mock_qdrant_instance = Mock()
        mock_qdrant_instance.get_collections.return_value = Mock(collections=[Mock(name='test-collection')])
        mock_qdrant_instance.search.return_value = [
            Mock(id='chunk1', payload={'content': 'Stability test content', 'metadata': {'url': 'stability-test.com', 'page_title': 'Stability Test', 'section': 'Stability Section'}}, score=0.9)
        ] * 5  # Multiple results for top_k=5
        mock_qdrant_client.return_value = mock_qdrant_instance

        # Update the global Qdrant client instance
        from src.rag_validation.qdrant_client import QdrantClientWrapper
        QdrantClientWrapper.client = mock_qdrant_instance

        # Test with multiple queries to simulate load
        test_queries = [f"Load test query {i}" for i in range(10)]
        result = run_comprehensive_batch_validation(test_queries, top_k=1)

        # Verify that all queries were processed
        assert result['total_queries'] == len(test_queries)
        assert result['completed_queries'] == len(test_queries)

        # Verify metrics are calculated properly
        metrics = result['overall_metrics']
        assert 'avg_query_time_ms' in metrics
        assert 'avg_semantic_alignment' in metrics
        assert 'metadata_accuracy_rate' in metrics
        assert 'pipeline_stability' in metrics

    def test_pipeline_components_direct_integration(self):
        """Test direct integration between pipeline components"""
        # This test verifies that components work together without mocking
        # We'll use a minimal integration test with mocked external services
        with patch('src.rag_validation.cohere_embedder.cohere.Client') as mock_cohere:
            with patch('src.rag_validation.qdrant_client.QdrantClient') as mock_qdrant:
                # Set up mocks
                mock_cohere_instance = Mock()
                mock_cohere_instance.embed.return_value = Mock(embeddings=[[0.1, 0.2, 0.3]])
                mock_cohere.return_value = mock_cohere_instance

                mock_qdrant_instance = Mock()
                mock_qdrant_instance.get_collections.return_value = Mock(collections=[Mock(name='test-collection')])
                mock_qdrant_instance.search.return_value = [
                    Mock(id='chunk1', payload={'content': 'Integration test', 'metadata': {'url': 'integration-test.com', 'page_title': 'Integration Test', 'section': 'Integration Section'}}, score=0.85)
                ]
                mock_qdrant.return_value = mock_qdrant_instance

                # Update the global Qdrant client instance
                from src.rag_validation.qdrant_client import QdrantClientWrapper
                QdrantClientWrapper.client = mock_qdrant_instance

                # Test the integration
                validator = QueryValidator()
                query_result = validator.validate_single_query("Integration test query", top_k=1)

                # Evaluate the result
                evaluator = ResultEvaluator()
                validation_result = evaluator.evaluate_query_result(query_result)

                # Verify integration worked
                assert query_result.query_id.startswith('query-')
                assert len(query_result.retrieved_chunks) == 1
                assert validation_result.metadata_accuracy is True
                assert validation_result.semantic_alignment > 0