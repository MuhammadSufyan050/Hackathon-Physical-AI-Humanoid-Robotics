"""Unit tests for the Book Q&A Agent."""

import unittest
from unittest.mock import Mock, patch
import os
from src.agents.book_qna_agent import BookQnaAgent
from src.models.query import Question, Answer
from src.models.document import RetrievedChunk


class TestBookQnaAgent(unittest.TestCase):
    """Unit tests for the BookQnaAgent class."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        # Set up environment variables for testing
        os.environ['OPENAI_API_KEY'] = 'test-key'
        os.environ['COHERE_API_KEY'] = 'test-key'
        os.environ['QDRANT_URL'] = 'https://test.qdrant.io'

        # Mock the external dependencies to avoid actual API calls
        with patch('src.agents.book_qna_agent.OpenAI'), \
             patch('src.agents.book_qna_agent.QdrantService'), \
             patch('src.agents.book_qna_agent.EmbeddingService'):

            self.agent = BookQnaAgent()

    def test_agent_initialization(self):
        """Test that the agent initializes correctly."""
        self.assertIsNotNone(self.agent)
        # Mocks ensure initialization succeeds without real API calls

    def test_question_creation(self):
        """Test that questions can be created properly."""
        question = Question.create("Test question?", "test_user")

        self.assertEqual(question.content, "Test question?")
        self.assertEqual(question.user_id, "test_user")
        self.assertIsNotNone(question.id)
        self.assertIsNotNone(question.timestamp)

    def test_answer_creation(self):
        """Test that answers can be created properly."""
        chunk = RetrievedChunk.create(
            content="Test content",
            score=0.8,
            metadata={}
        )

        answer = Answer.create(
            question_id="test_id",
            content="Test answer",
            source_chunks=[chunk],
            confidence=0.8,
            generated_by="test_model"
        )

        self.assertEqual(answer.question_id, "test_id")
        self.assertEqual(answer.content, "Test answer")
        self.assertEqual(len(answer.source_chunks), 1)
        self.assertEqual(answer.confidence, 0.8)
        self.assertEqual(answer.generated_by, "test_model")

    def test_retrieved_chunk_creation(self):
        """Test that retrieved chunks can be created properly."""
        chunk = RetrievedChunk.create(
            content="Test content",
            score=0.8,
            metadata={"source": "test"}
        )

        self.assertEqual(chunk.content, "Test content")
        self.assertEqual(chunk.score, 0.8)
        self.assertEqual(chunk.metadata["source"], "test")
        self.assertIsNotNone(chunk.id)

    def test_question_validation(self):
        """Test question validation."""
        question = Question.create("Valid question", "test_user")

        # Should not raise an exception
        question.validate()

        # Test with empty content
        with self.assertRaises(ValueError):
            empty_question = Question.create("", "test_user")
            empty_question.validate()

        # Test with short content
        with self.assertRaises(ValueError):
            short_question = Question.create("Hi", "test_user")
            short_question.validate()


if __name__ == '__main__':
    unittest.main()