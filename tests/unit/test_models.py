"""Unit tests for the data models."""

import unittest
from datetime import datetime
from src.models.query import Question, QueryEmbedding, Answer
from src.models.document import RetrievedChunk, SourceMetadata


class TestQuestionModel(unittest.TestCase):
    """Unit tests for the Question model."""

    def test_question_creation(self):
        """Test that questions can be created properly."""
        question = Question.create("Test question?", "test_user")

        self.assertEqual(question.content, "Test question?")
        self.assertEqual(question.user_id, "test_user")
        self.assertIsNotNone(question.id)
        self.assertIsNotNone(question.timestamp)

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

    def test_question_factory_method(self):
        """Test the Question.create factory method."""
        question = Question.create("Test content", "test_user")

        self.assertEqual(question.content, "Test content")
        self.assertEqual(question.user_id, "test_user")
        self.assertTrue(isinstance(question.timestamp, datetime))


class TestQueryEmbeddingModel(unittest.TestCase):
    """Unit tests for the QueryEmbedding model."""

    def test_query_embedding_creation(self):
        """Test that query embeddings can be created properly."""
        embedding = QueryEmbedding.create("test_id", [0.1, 0.2, 0.3], "test_model")

        self.assertEqual(embedding.question_id, "test_id")
        self.assertEqual(embedding.embedding, [0.1, 0.2, 0.3])
        self.assertEqual(embedding.model, "test_model")
        self.assertIsNotNone(embedding.timestamp)

    def test_query_embedding_validation(self):
        """Test query embedding validation."""
        embedding = QueryEmbedding.create("test_id", [0.1, 0.2, 0.3], "test_model")

        # Should not raise an exception
        embedding.validate()

        # Test with empty embedding
        with self.assertRaises(ValueError):
            invalid_embedding = QueryEmbedding.create("test_id", [], "test_model")
            invalid_embedding.validate()


class TestAnswerModel(unittest.TestCase):
    """Unit tests for the Answer model."""

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

    def test_answer_validation(self):
        """Test answer validation."""
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

        # Should not raise an exception
        answer.validate()

        # Test with empty content
        with self.assertRaises(ValueError):
            invalid_answer = Answer.create(
                question_id="test_id",
                content="",
                source_chunks=[chunk],
                confidence=0.8,
                generated_by="test_model"
            )
            invalid_answer.validate()

        # Test with no source chunks
        with self.assertRaises(ValueError):
            invalid_answer = Answer.create(
                question_id="test_id",
                content="Test answer",
                source_chunks=[],
                confidence=0.8,
                generated_by="test_model"
            )
            invalid_answer.validate()

    def test_answer_source_methods(self):
        """Test answer source-related methods."""
        chunk1 = RetrievedChunk.create(
            content="Test content 1",
            score=0.8,
            metadata={"source_url": "https://example1.com"}
        )
        chunk2 = RetrievedChunk.create(
            content="Test content 2",
            score=0.9,
            metadata={"source_url": "https://example2.com"}
        )

        answer = Answer.create(
            question_id="test_id",
            content="Test answer",
            source_chunks=[chunk1, chunk2],
            confidence=0.8,
            generated_by="test_model"
        )

        self.assertTrue(answer.has_sufficient_sources())
        urls = answer.get_source_urls()
        self.assertIn("https://example1.com", urls)
        self.assertIn("https://example2.com", urls)
        self.assertEqual(len(urls), 2)


class TestRetrievedChunkModel(unittest.TestCase):
    """Unit tests for the RetrievedChunk model."""

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

    def test_retrieved_chunk_validation(self):
        """Test retrieved chunk validation."""
        chunk = RetrievedChunk.create(
            content="Test content",
            score=0.8,
            metadata={}
        )

        # Should not raise an exception
        chunk.validate()

        # Test with empty content
        with self.assertRaises(ValueError):
            invalid_chunk = RetrievedChunk.create(
                content="",
                score=0.8,
                metadata={}
            )
            invalid_chunk.validate()

    def test_retrieved_chunk_methods(self):
        """Test retrieved chunk methods."""
        chunk = RetrievedChunk.create(
            content="Test content",
            score=0.8,
            metadata={}
        )

        # Test is_relevant method
        self.assertTrue(chunk.is_relevant(0.5))
        self.assertFalse(chunk.is_relevant(0.9))

        # Test get_source_metadata method
        metadata = chunk.get_source_metadata()
        self.assertIsInstance(metadata, SourceMetadata)
        self.assertEqual(metadata.relevance_score, 0.8)


class TestSourceMetadataModel(unittest.TestCase):
    """Unit tests for the SourceMetadata model."""

    def test_source_metadata_creation(self):
        """Test that source metadata can be created properly."""
        metadata = SourceMetadata(
            source_url="https://example.com",
            page_number=42,
            relevance_score=0.8
        )

        self.assertEqual(metadata.source_url, "https://example.com")
        self.assertEqual(metadata.page_number, 42)
        self.assertEqual(metadata.relevance_score, 0.8)

    def test_source_metadata_validation(self):
        """Test source metadata validation."""
        # Valid metadata should pass
        valid_metadata = SourceMetadata(
            source_url="https://example.com",
            page_number=42,
            relevance_score=0.8
        )
        valid_metadata.validate()

        # Invalid relevance score
        with self.assertRaises(ValueError):
            invalid_metadata = SourceMetadata(
                source_url="https://example.com",
                relevance_score=1.5
            )
            invalid_metadata.validate()

        # No source identification
        with self.assertRaises(ValueError):
            invalid_metadata = SourceMetadata(
                relevance_score=0.8
            )
            invalid_metadata.validate()

    def test_source_metadata_identification(self):
        """Test source metadata identification methods."""
        metadata_with_url = SourceMetadata(
            source_url="https://example.com",
            relevance_score=0.8
        )
        self.assertTrue(metadata_with_url.has_sufficient_identification())

        metadata_with_page = SourceMetadata(
            page_number=42,
            relevance_score=0.8
        )
        self.assertTrue(metadata_with_page.has_sufficient_identification())

        metadata_with_section = SourceMetadata(
            section_title="Test Section",
            relevance_score=0.8
        )
        self.assertTrue(metadata_with_section.has_sufficient_identification())

        # Empty metadata should not have sufficient identification
        empty_metadata = SourceMetadata(relevance_score=0.8)
        self.assertFalse(empty_metadata.has_sufficient_identification())


if __name__ == '__main__':
    unittest.main()