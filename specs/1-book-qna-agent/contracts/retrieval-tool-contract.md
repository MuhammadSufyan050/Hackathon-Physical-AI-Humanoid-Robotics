# Tool Contract: Qdrant Retrieval Tool

## Overview
Contract for the Qdrant retrieval tool that will be registered with the OpenAI Assistant. This tool enables semantic search of book content stored in Qdrant.

## Tool Definition

### Function Signature
```json
{
  "name": "retrieve_book_content",
  "description": "Retrieve relevant content from book collection based on semantic similarity to the user's query",
  "parameters": {
    "type": "object",
    "properties": {
      "query": {
        "type": "string",
        "description": "The user's question or query to search for relevant content"
      },
      "top_k": {
        "type": "number",
        "description": "Number of top results to return (default: 5, max: 10)",
        "default": 5,
        "minimum": 1,
        "maximum": 10
      },
      "min_score": {
        "type": "number",
        "description": "Minimum relevance score threshold (default: 0.5, range: 0.0-1.0)",
        "default": 0.5,
        "minimum": 0.0,
        "maximum": 1.0
      }
    },
    "required": ["query"]
  }
}
```

### Expected Input
- `query`: The user's natural language question to find relevant book content for
- `top_k`: (Optional) Number of content chunks to retrieve (1-10, defaults to 5)
- `min_score`: (Optional) Minimum similarity threshold (0.0-1.0, defaults to 0.5)

### Expected Output
```json
{
  "type": "object",
  "properties": {
    "results": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "id": {"type": "string", "description": "Unique identifier for the content chunk"},
          "content": {"type": "string", "description": "The text content of the chunk"},
          "score": {"type": "number", "description": "Similarity score between 0 and 1"},
          "source_url": {"type": "string", "description": "URL or reference to the source"},
          "page_number": {"type": "number", "description": "Page number in the book"},
          "section_title": {"type": "string", "description": "Title of the section"},
          "metadata": {
            "type": "object",
            "description": "Additional metadata about the content chunk"
          }
        },
        "required": ["id", "content", "score"]
      }
    },
    "query_embedding_used": {
      "type": "array",
      "items": {"type": "number"},
      "description": "The embedding vector used for the search"
    }
  },
  "required": ["results"]
}
```

## Error Handling

### Possible Errors
1. **ConnectionError**: Unable to connect to Qdrant service
   - Response: `{"error": "Unable to connect to content database", "code": "CONNECTION_ERROR"}`

2. **AuthenticationError**: Invalid credentials for Qdrant
   - Response: `{"error": "Authentication failed with content database", "code": "AUTH_ERROR"}`

3. **InvalidQueryError**: Query is too short or malformed
   - Response: `{"error": "Invalid query provided", "code": "INVALID_QUERY"}`

4. **NoResultsError**: No content found matching the query
   - Response: `{"results": [], "message": "No relevant content found"}`

## Performance Requirements
- Tool should return results within 5 seconds
- Tool should handle queries up to 1000 characters in length
- Tool should support concurrent usage by multiple agents

## Integration Points
- Called by: OpenAI Assistant when it determines semantic search is needed
- Calls: Qdrant Cloud service via qdrant-client
- Uses: Cohere API for generating query embeddings