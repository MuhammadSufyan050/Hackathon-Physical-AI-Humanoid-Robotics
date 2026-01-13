"""Data models for documents and metadata."""

from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


class SourceMetadata(BaseModel):
    """Represents information about where in the book content the answer information originated."""

    source_url: Optional[str] = Field(default=None, description="URL reference to the source")
    page_number: Optional[int] = Field(default=None, description="Page number in the book")
    section_title: Optional[str] = Field(default=None, description="Title of the section")
    chapter_title: Optional[str] = Field(default=None, description="Title of the chapter")
    book_title: Optional[str] = Field(default=None, description="Title of the book")
    relevance_score: float = Field(default=0.0, description="Relevance score of this source to the question")

    def validate(self) -> bool:
        """Validate the source metadata."""
        if self.relevance_score < 0.0 or self.relevance_score > 1.0:
            raise ValueError("Relevance score must be between 0.0 and 1.0")

        # At least one source identifier must be provided
        if not any([
            self.source_url,
            self.page_number,
            self.section_title
        ]):
            raise ValueError("At least one source identifier (URL, page number, or section title) must be provided")

        return True

    def has_sufficient_identification(self) -> bool:
        """Check if the metadata has sufficient identification information."""
        return any([
            self.source_url,
            self.page_number,
            self.section_title
        ])


class RetrievedChunk(BaseModel):
    """Represents a text chunk retrieved from Qdrant based on semantic similarity."""

    id: str = Field(description="Unique identifier for the chunk")
    content: str = Field(description="The text content of the chunk")
    score: float = Field(description="Similarity score from vector search")
    metadata: Dict[str, Any] = Field(description="Additional metadata (source, page, etc.)")
    source_url: Optional[str] = Field(default=None, description="URL or reference to the source")
    page_number: Optional[int] = Field(default=None, description="Page number if applicable")
    section_title: Optional[str] = Field(default=None, description="Section title if applicable")
    embedding: Optional[List[float]] = Field(default=None, description="The embedding vector of the chunk")

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    @classmethod
    def create(
        cls,
        content: str,
        score: float,
        metadata: Dict[str, Any],
        chunk_id: Optional[str] = None
    ) -> "RetrievedChunk":
        """Create a new RetrievedChunk instance."""
        import uuid
        return cls(
            id=chunk_id or str(uuid.uuid4()),
            content=content,
            score=score,
            metadata=metadata,
            source_url=metadata.get("source_url"),
            page_number=metadata.get("page_number"),
            section_title=metadata.get("section_title")
        )

    def validate(self) -> bool:
        """Validate the retrieved chunk."""
        if not self.content or not self.content.strip():
            raise ValueError("Content cannot be empty")

        if not 0.0 <= self.score <= 1.0:
            raise ValueError("Score must be between 0.0 and 1.0")

        return True

    def get_source_metadata(self) -> SourceMetadata:
        """Extract source metadata from the chunk."""
        return SourceMetadata(
            source_url=self.source_url,
            page_number=self.page_number,
            section_title=self.section_title,
            relevance_score=self.score
        )

    def is_relevant(self, min_score: float = 0.5) -> bool:
        """Check if the chunk is relevant based on the minimum score threshold."""
        return self.score >= min_score