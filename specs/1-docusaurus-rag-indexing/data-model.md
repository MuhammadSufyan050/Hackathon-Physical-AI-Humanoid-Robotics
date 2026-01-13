# Data Model: Docusaurus Book Content for RAG Indexing

## Entities

### BookContent
**Description**: Represents the extracted content from a Docusaurus book
**Fields**:
- url (string): The source URL of the content
- title (string): The title of the page/chapter
- text_content (string): The extracted text content
- metadata (object): Additional metadata about the content
  - created_at (timestamp): When the content was extracted
  - source_type (string): Type of source (e.g., "docusaurus_page")
  - section_hierarchy (array): Hierarchy of sections (e.g., ["Chapter 1", "Section 1.1"])

### EmbeddingVector
**Description**: The semantic vector representation of a text segment
**Fields**:
- vector (array[float]): The embedding vector values
- model_name (string): The name of the model used to generate the embedding
- model_version (string): The version of the model used

### IndexRecord
**Description**: A stored entry in the vector database containing the embedding vector, original content, and metadata
**Fields**:
- id (string): Unique identifier for the record
- vector (array[float]): The embedding vector
- payload (object): Metadata and original content
  - text (string): Original text content
  - url (string): Source URL
  - title (string): Content title
  - metadata (object): Additional metadata
    - created_at (timestamp)
    - source_type (string)
    - section_hierarchy (array)

### DocusaurusBook
**Description**: Represents a deployed Docusaurus book
**Fields**:
- base_url (string): The base URL of the Docusaurus site
- title (string): The title of the book/site
- urls (array[string]): List of all page URLs in the book
- metadata (object): Additional metadata about the book
  - last_indexed_at (timestamp): When the book was last processed
  - total_pages (integer): Number of pages in the book
  - status (string): Current status (e.g., "indexed", "indexing", "failed")

## Relationships

- One DocusaurusBook contains many BookContent items
- One BookContent generates one EmbeddingVector
- One EmbeddingVector becomes one IndexRecord in the vector database

## Validation Rules

### BookContent
- url must be a valid URL format
- text_content must not be empty
- metadata must include required fields

### EmbeddingVector
- vector must have consistent dimensions (e.g., 1024 for Cohere models)
- model_name must be specified
- vector values must be valid floats

### IndexRecord
- id must be unique
- vector must match collection dimensions
- payload must contain required fields (text, url)

### DocusaurusBook
- base_url must be a valid URL
- urls must all be valid and related to the base URL
- status must be one of allowed values

## State Transitions

### DocusaurusBook Status
- "pending" → "indexing" when processing begins
- "indexing" → "indexed" when all content is successfully processed
- "indexing" → "failed" when processing encounters errors
- "indexed" → "indexing" when re-indexing is triggered