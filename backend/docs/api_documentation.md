# Qdrant Retrieval Validation API Documentation

## Overview

The Qdrant Retrieval Validation API provides endpoints to test and validate the Qdrant retrieval pipeline for a book-focused RAG system. It allows for connection testing, semantic search validation, and comprehensive batch validation.

## Endpoints

### GET /api/v1/validate/connection
Test connection to Qdrant Cloud

#### Description
Verify that the system can connect to Qdrant Cloud successfully

#### Response
```json
{
  "success": true,
  "message": "Successfully connected to Qdrant Cloud",
  "response_time_ms": 150
}
```

#### Error Response
```json
{
  "success": false,
  "error": "Failed to connect to Qdrant Cloud",
  "response_time_ms": 2000
}
```

### POST /api/v1/validate/query
Validate a single query against Qdrant

#### Description
Execute a query against Qdrant and return validation metrics

#### Request Body
```json
{
  "query": "What is ROS2?",
  "top_k": 5,
  "validate_embedding": true
}
```

#### Response
```json
{
  "query_id": "query-123abc",
  "original_query": "What is ROS2?",
  "retrieved_chunks": [
    {
      "id": "chunk-456def",
      "content": "ROS2 (Robot Operating System 2) is a flexible framework for writing robot software...",
      "metadata": {
        "url": "https://example.com/ros2-introduction",
        "page_title": "Introduction to ROS2",
        "section": "What is ROS2?",
        "source_file": "chapter_3_ros2_fundamentals.md"
      },
      "similarity_score": 0.87
    }
  ],
  "validation_result": null,
  "retrieval_time_ms": 1200
}
```

#### Error Response
```json
{
  "error": "Query text is required"
}
```

### POST /api/v1/validate/batch
Run batch validation

#### Description
Execute multiple test queries and return comprehensive validation report

#### Request Body
```json
{
  "queries": ["What is ROS2?", "Explain Gazebo simulation", "How to use Isaac Sim?"],
  "top_k": 5,
  "validation_config": {
    "top_k": 5,
    "validation_threshold": 0.7,
    "max_retries": 3
  }
}
```

#### Response
```json
{
  "batch_id": "batch-456",
  "total_queries": 3,
  "completed_queries": 3,
  "overall_metrics": {
    "connection_success_rate": 0.99,
    "avg_query_time_ms": 1200.5,
    "avg_semantic_alignment": 0.82,
    "metadata_accuracy_rate": 1.0,
    "pipeline_stability": "consistent"
  },
  "detailed_results": [
    {
      "query": "What is ROS2?",
      "validation_result": {
        "precision_at_k": 0.85,
        "recall_at_k": 0.78,
        "relevance_score": 0.82,
        "semantic_alignment": 0.84,
        "metadata_accuracy": true
      },
      "retrieved_count": 5
    }
  ],
  "execution_time_ms": 5400
}
```

## Configuration

The validation API uses the following configuration parameters from environment variables:

- `QDRANT_HOST`: Qdrant host URL
- `QDRANT_API_KEY`: Qdrant API key
- `QDRANT_COLLECTION_NAME`: Name of the Qdrant collection to query
- `COHERE_API_KEY`: Cohere API key
- `TOP_K`: Number of results to retrieve for each query (default: 5)
- `VALIDATION_THRESHOLD`: Minimum relevance score for acceptable results (default: 0.7)
- `MAX_RETRIES`: Maximum number of retry attempts for failed queries (default: 3)
- `COHERE_MODEL`: Name of the Cohere model to use for embeddings (default: embed-english-v3.0)

## Error Handling

The API includes comprehensive error handling with:

- Connection retries with exponential backoff
- Rate limit handling for Cohere API
- Graceful degradation when services are unavailable
- Detailed error messages for debugging

## Performance Monitoring

The API tracks and reports:

- Query response times
- Embedding generation times
- Connection validation times
- Overall system performance metrics