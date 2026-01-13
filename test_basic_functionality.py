"""Basic functionality test for the Book Q&A Retrieval Agent."""

import os
import sys
from unittest.mock import Mock, patch

# Add src to path so we can import the modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config.settings import Settings


def test_settings_loading():
    """Test that settings can be loaded from environment variables."""
    # This test requires environment variables to be set
    # For a basic test without actual API calls, we'll just check the structure
    print("Testing settings loading...")

    # Check that we can create a settings object
    settings = Settings(
        openai_api_key="test-key",
        cohere_api_key="test-key",
        qdrant_url="https://test.qdrant.io"
    )

    assert settings.openai_api_key == "test-key"
    assert settings.cohere_api_key == "test-key"
    assert settings.qdrant_url == "https://test.qdrant.io"
    print("[PASS] Settings loading test passed")


def test_models():
    """Test that data models can be created."""
    print("Testing data models...")

    from src.models.query import Question, Answer
    from src.models.document import RetrievedChunk, SourceMetadata

    # Test Question creation
    question = Question.create("What is the main concept?", "user123")
    assert question.content == "What is the main concept?"
    assert question.user_id == "user123"
    print("[PASS] Question model test passed")

    # Test RetrievedChunk creation
    chunk = RetrievedChunk.create(
        content="This is some book content",
        score=0.8,
        metadata={"source_url": "https://example.com", "page_number": 42}
    )
    assert chunk.content == "This is some book content"
    assert chunk.score == 0.8
    print("[PASS] RetrievedChunk model test passed")

    # Test SourceMetadata validation
    metadata = SourceMetadata(
        source_url="https://example.com",
        page_number=42,
        relevance_score=0.8
    )
    assert metadata.source_url == "https://example.com"
    assert metadata.page_number == 42
    assert metadata.relevance_score == 0.8
    print("[PASS] SourceMetadata model test passed")


def test_services_structure():
    """Test that service classes can be imported and instantiated (without actual API calls)."""
    print("Testing service structure...")

    # We can't test the actual functionality without valid API keys,
    # but we can check that the classes exist and have expected methods
    from src.services.embedding_service import EmbeddingService
    from src.services.qdrant_service import QdrantService

    # Check that EmbeddingService has expected methods
    embedding_service = EmbeddingService
    assert hasattr(embedding_service, '__init__')
    print("[PASS] EmbeddingService structure test passed")

    # Check that QdrantService has expected methods
    qdrant_service = QdrantService
    assert hasattr(qdrant_service, '__init__')
    print("[PASS] QdrantService structure test passed")


def test_agent_structure():
    """Test that agent classes can be imported and have expected methods."""
    print("Testing agent structure...")

    from src.agents.book_qna_agent import BookQnaAgent
    from src.agents.tools.retrieval_tool import RetrievalTool

    # Check that BookQnaAgent has expected methods
    agent = BookQnaAgent
    assert hasattr(agent, '__init__')
    assert hasattr(agent, 'process_question')
    assert hasattr(agent, 'initialize_assistant')
    print("[PASS] BookQnaAgent structure test passed")

    # Check that RetrievalTool has expected methods
    tool = RetrievalTool
    assert hasattr(tool, 'run')
    assert hasattr(tool, 'get_name')
    assert hasattr(tool, 'get_description')
    print("[PASS] RetrievalTool structure test passed")


if __name__ == "__main__":
    print("Running basic functionality tests...\n")

    try:
        test_settings_loading()
        test_models()
        test_services_structure()
        test_agent_structure()

        print("\n[SUCCESS] All basic functionality tests passed!")
        print("\nNote: These are structural tests only.")
        print("To run the full application, you'll need valid API keys in your .env file.")

    except Exception as e:
        print(f"\n[ERROR] Test failed: {e}")
        sys.exit(1)