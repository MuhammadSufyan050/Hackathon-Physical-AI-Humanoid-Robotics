"""Book Q&A Retrieval Agent implementation."""

import logging
from typing import Dict, Any, Optional, List
from openai import OpenAI
from src.config.settings import settings, validate_settings
from src.services.qdrant_service import QdrantService
from src.services.embedding_service import EmbeddingService
from src.models.query import Question, QueryEmbedding, Answer
from src.models.document import RetrievedChunk
from src.utils.error_handler import AgentError, ConnectionError, ConfigurationError


logger = logging.getLogger(__name__)


class BookQnaAgent:
    """Main agent class for book Q&A using OpenAI Assistants API with Qdrant retrieval."""

    def __init__(self):
        """Initialize the Book Q&A Agent with required services."""
        # Validate configuration
        try:
            validate_settings()
        except ValueError as e:
            raise ConfigurationError(f"Invalid configuration: {str(e)}")

        # Initialize OpenAI client
        try:
            self.openai_client = OpenAI(api_key=settings.openai_api_key)
        except Exception as e:
            raise ConnectionError(f"Failed to initialize OpenAI client: {str(e)}", service="OpenAI")

        # Initialize services
        try:
            self.qdrant_service = QdrantService()
            self.embedding_service = EmbeddingService()
        except Exception as e:
            raise ConnectionError(f"Failed to initialize services: {str(e)}")

        # Verify Qdrant connection
        if not self.qdrant_service.verify_connection():
            raise ConnectionError("Failed to connect to Qdrant collection", service="Qdrant")

        # Initialize agent state
        self.assistant_id: Optional[str] = None
        self.thread_id: Optional[str] = None

        logger.info("Book Q&A Agent initialized successfully")

    def initialize_assistant(self) -> str:
        """
        Initialize the OpenAI Assistant with retrieval capabilities.

        Returns:
            Assistant ID
        """
        try:
            # Import the retrieval tool here to avoid circular imports
            from .tools.retrieval_tool import RetrievalTool
            retrieval_tool = RetrievalTool()

            # Create or retrieve assistant with the retrieval tool
            assistant = self.openai_client.beta.assistants.create(
                name="Book Q&A Assistant",
                description="An assistant that answers questions based on book content using retrieval augmentation.",
                model="gpt-4-turbo",  # Using a capable model
                instructions=(
                    "You are a helpful assistant that answers questions based on provided book content. "
                    "Always provide answers based only on the retrieved content. "
                    "Include source references when possible. "
                    "If the answer is not available in the provided context, clearly state that you cannot answer based on the available content."
                ),
                tools=[retrieval_tool.register_with_assistant()]
            )

            self.assistant_id = assistant.id
            logger.info(f"Assistant created with ID: {self.assistant_id}")
            return self.assistant_id

        except Exception as e:
            logger.error(f"Error initializing assistant: {str(e)}")
            raise AgentError(f"Failed to initialize assistant: {str(e)}")

    def create_thread(self) -> str:
        """
        Create a new thread for conversation.

        Returns:
            Thread ID
        """
        try:
            thread = self.openai_client.beta.threads.create()
            self.thread_id = thread.id
            logger.info(f"Thread created with ID: {self.thread_id}")
            return self.thread_id

        except Exception as e:
            logger.error(f"Error creating thread: {str(e)}")
            raise AgentError(f"Failed to create thread: {str(e)}")

    def process_question(self, question_text: str, user_id: Optional[str] = None) -> Answer:
        """
        Process a user question and return an answer based on retrieved content.

        Args:
            question_text: The user's question
            user_id: Optional user identifier

        Returns:
            Answer object with the response and source information
        """
        try:
            # Create question object
            question = Question.create(content=question_text, user_id=user_id)
            question.validate()

            # Generate embedding for the question
            query_embedding = self.embedding_service.generate_embedding(question.content)
            embedding_obj = QueryEmbedding.create(
                question_id=question.id,
                embedding=query_embedding,
                model=settings.embedding_model
            )

            # Retrieve relevant content from Qdrant
            retrieved_chunks = self._retrieve_content(query_embedding)

            # Generate answer using retrieved content
            answer = self._generate_answer(question, retrieved_chunks)

            logger.info(f"Processed question with ID: {question.id}")
            return answer

        except Exception as e:
            logger.error(f"Error processing question: {str(e)}")
            raise

    def _retrieve_content(self, query_embedding: List[float]) -> List[RetrievedChunk]:
        """
        Retrieve relevant content chunks from Qdrant based on query embedding.

        Args:
            query_embedding: The embedding vector to search for

        Returns:
            List of retrieved content chunks
        """
        try:
            results = self.qdrant_service.search(
                query_vector=query_embedding,
                top_k=settings.top_k_results,
                min_score=settings.min_score_threshold
            )

            retrieved_chunks = []
            for result in results:
                chunk = RetrievedChunk.create(
                    content=result["content"],
                    score=result["score"],
                    metadata=result["metadata"],
                    chunk_id=result["id"]
                )
                retrieved_chunks.append(chunk)

            logger.info(f"Retrieved {len(retrieved_chunks)} relevant chunks")
            return retrieved_chunks

        except Exception as e:
            logger.error(f"Error retrieving content: {str(e)}")
            raise

    def _generate_answer(self, question: Question, retrieved_chunks: List[RetrievedChunk]) -> Answer:
        """
        Generate an answer based on the question and retrieved content.

        Args:
            question: The original question
            retrieved_chunks: List of retrieved content chunks

        Returns:
            Answer object with the response
        """
        try:
            if not retrieved_chunks:
                # Handle case where no relevant content was found
                content = "I cannot answer this question based on the available book content."
                confidence = 0.0
            else:
                # Prepare context from retrieved chunks
                context_parts = []
                for chunk in retrieved_chunks:
                    context_parts.append(f"Source: {chunk.source_url or 'Unknown'}")
                    context_parts.append(f"Content: {chunk.content}")
                    context_parts.append("---")

                context = "\n".join(context_parts)

                # Generate answer using OpenAI
                prompt = f"""
                Based on the following book content, please answer the question:

                BOOK CONTENT:
                {context}

                QUESTION:
                {question.content}

                INSTRUCTIONS:
                - Answer based only on the provided book content
                - Include source references from the book content
                - If the answer is not available in the provided content, say so explicitly
                - Do not make up information not present in the content
                """

                response = self.openai_client.chat.completions.create(
                    model="gpt-4-turbo",
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that answers questions based only on provided book content. Always cite sources and never make up information."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.3
                )

                content = response.choices[0].message.content
                # Calculate confidence based on number and relevance of retrieved chunks
                avg_score = sum(chunk.score for chunk in retrieved_chunks) / len(retrieved_chunks) if retrieved_chunks else 0.0
                confidence = min(avg_score, 1.0)  # Cap at 1.0

            # Create answer object
            answer = Answer.create(
                question_id=question.id,
                content=content,
                source_chunks=retrieved_chunks,
                confidence=confidence,
                generated_by="gpt-4-turbo"
            )

            answer.validate()
            return answer

        except Exception as e:
            logger.error(f"Error generating answer: {str(e)}")
            raise

    def check_connection(self) -> Dict[str, bool]:
        """
        Check connectivity to all required services.

        Returns:
            Dictionary with connection status for each service
        """
        status = {
            "openai": False,
            "qdrant": False,
            "cohere": False
        }

        try:
            # Test OpenAI connection by making a simple call
            self.openai_client.models.list()
            status["openai"] = True
        except Exception:
            logger.warning("OpenAI connection failed")

        try:
            # Test Qdrant connection
            status["qdrant"] = self.qdrant_service.verify_connection()
        except Exception:
            logger.warning("Qdrant connection failed")

        try:
            # Test Cohere connection by generating a simple embedding
            self.embedding_service.generate_embedding("test")
            status["cohere"] = True
        except Exception:
            logger.warning("Cohere connection failed")

        return status

    def close(self):
        """Clean up resources."""
        logger.info("Closing Book Q&A Agent")
        # Any cleanup code would go here