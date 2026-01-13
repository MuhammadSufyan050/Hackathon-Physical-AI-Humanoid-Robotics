from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Query:
    """
    User input text that is converted to a vector using Cohere embeddings for semantic search;
    contains the search intent and context related to book content
    """
    id: str
    text: str
    embedding: Optional[List[float]] = None
    category: Optional[str] = None
    expected_topics: Optional[List[str]] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()


@dataclass
class TextChunk:
    """
    Segments of book content that have been processed and stored as vectors in Qdrant Cloud using Cohere embeddings;
    represents a unit of retrievable information
    """
    id: str
    content: str
    vector: Optional[List[float]] = None
    metadata: Dict[str, str] = None
    created_at: datetime = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.metadata is None:
            self.metadata = {}


@dataclass
class QueryResult:
    """
    Result of a query against the Qdrant database, containing retrieved chunks and their similarity scores
    """
    query_id: str
    retrieved_chunks: List[TextChunk]
    similarity_scores: List[float]
    retrieval_time_ms: float
    top_k: int
    executed_at: datetime = None

    def __post_init__(self):
        if self.executed_at is None:
            self.executed_at = datetime.now()


@dataclass
class ValidationResult:
    """
    Evaluation of the relevance and accuracy of query results
    """
    query_result_id: str
    precision_at_k: float
    recall_at_k: float
    relevance_score: float
    semantic_alignment: float
    metadata_accuracy: bool
    evaluated_at: datetime = None

    def __post_init__(self):
        if self.evaluated_at is None:
            self.evaluated_at = datetime.now()


@dataclass
class ValidationConfigEntity:
    """
    Configuration parameters for the validation process (separate from settings config)
    """
    top_k: int = 5
    cohere_model: str = "embed-english-v3.0"
    qdrant_collection: str = "rag_embedding"
    validation_threshold: float = 0.7
    max_retries: int = 3