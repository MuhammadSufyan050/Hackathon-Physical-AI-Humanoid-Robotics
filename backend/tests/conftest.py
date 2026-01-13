"""
Configuration for pytest test suite
"""
import os
import pytest
from unittest.mock import patch


def pytest_configure(config):
    """Configure pytest"""
    # Set up environment variables for testing
    os.environ.setdefault('COHERE_API_KEY', 'test-cohere-key')
    os.environ.setdefault('QDRANT_HOST', 'test-host')
    os.environ.setdefault('QDRANT_API_KEY', 'test-key')
    os.environ.setdefault('QDRANT_COLLECTION_NAME', 'test-collection')
    os.environ.setdefault('VALIDATION_THRESHOLD', '0.7')
    os.environ.setdefault('TOP_K', '5')
    os.environ.setdefault('MAX_RETRIES', '3')


@pytest.fixture(autouse=True)
def setup_test_environment():
    """
    Auto-used fixture to ensure proper test environment setup
    """
    # Ensure required environment variables are set
    required_vars = [
        'COHERE_API_KEY',
        'QDRANT_HOST',
        'QDRANT_API_KEY',
        'QDRANT_COLLECTION_NAME'
    ]

    for var in required_vars:
        if not os.getenv(var):
            os.environ[var] = f'test-{var.lower()}-value'

    yield  # This is where the test runs

    # Cleanup if needed
    pass


@pytest.fixture
def mock_cohere_client():
    """Fixture to mock Cohere client"""
    with patch('src.rag_validation.cohere_embedder.cohere.Client') as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.embed.return_value = type('obj', (object,), {
            'embeddings': [[0.1, 0.2, 0.3]]
        })()
        yield mock_instance


@pytest.fixture
def mock_qdrant_client():
    """Fixture to mock Qdrant client"""
    with patch('src.rag_validation.qdrant_client.QdrantClient') as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.get_collections.return_value = type('obj', (object,), {
            'collections': [type('obj', (object,), {'name': 'test-collection'})()]
        })()
        mock_instance.search.return_value = [
            type('obj', (object,), {
                'id': 'test-id',
                'payload': {'content': 'test content', 'metadata': {'url': 'test.com'}},
                'score': 0.9
            })()
        ]
        yield mock_instance


@pytest.fixture
def sample_text_chunks():
    """Fixture providing sample text chunks for testing"""
    from src.rag_validation.entities import TextChunk

    chunks = [
        TextChunk(
            id="chunk1",
            content="This is the first test chunk",
            metadata={
                'url': 'https://example.com/page1',
                'page_title': 'Example Page 1',
                'section': 'Introduction'
            }
        ),
        TextChunk(
            id="chunk2",
            content="This is the second test chunk",
            metadata={
                'url': 'https://example.com/page2',
                'page_title': 'Example Page 2',
                'section': 'Main Content'
            }
        )
    ]
    return chunks


@pytest.fixture
def sample_query_result(sample_text_chunks):
    """Fixture providing a sample query result for testing"""
    from src.rag_validation.entities import QueryResult

    result = QueryResult(
        query_id="test-query-123",
        retrieved_chunks=sample_text_chunks,
        similarity_scores=[0.9, 0.8],
        retrieval_time_ms=100.0,
        top_k=2
    )
    return result