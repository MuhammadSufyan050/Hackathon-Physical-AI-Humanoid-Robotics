# Quickstart: Qdrant Retrieval Pipeline Validation

## Prerequisites

- Python 3.11+
- Qdrant Cloud account and collection (from Spec-1)
- Cohere API key
- Environment with network access to Qdrant Cloud and Cohere API

## Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r backend/requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root with the following:

```env
# Cohere API Configuration
COHERE_API_KEY="your-cohere-api-key-here"

# Qdrant Vector Database Configuration
# For cloud instance:
QDRANT_URL="https://your-qdrant-cluster-url.qdrant.tech:6333"
QDRANT_API_KEY="your-qdrant-api-key-here"
QDRANT_HOST="your-qdrant-cluster-url.qdrant.tech"  # Alternative format for qdrant-client

# For local instance (alternative to cloud):
# QDRANT_HOST=localhost
# QDRANT_PORT=6333

# Application Configuration
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
MODEL_NAME=embed-english-v3.0

# Validation Configuration
QDRANT_COLLECTION_NAME="your-collection-name"
TOP_K=5
VALIDATION_THRESHOLD=0.7
MAX_RETRIES=3
COHERE_MODEL=embed-english-v3.0
```

## Validation Process

### 1. Run Basic Connection Test
```bash
cd backend
python -m scripts.validate_connection
```

### 2. Run Sample Query Validation
```bash
cd backend
python -m scripts.validate_retrieval sample-query "What is ROS2?"
```

### 3. Run Full Validation Suite
```bash
cd backend
python -m scripts.validate_retrieval run-all-tests
```

### 4. Generate Validation Report
```bash
cd backend
python -m scripts.validate_retrieval generate-report
```

### 5. Verify Configuration
```bash
cd backend
python -m scripts.validate_retrieval verify-config
```

## Key Components

### Configuration
- `backend/src/config/settings.py`: Manages all configuration and environment variables
- `ValidationConfig` class defines validation parameters

### Qdrant Client
- `backend/src/rag_validation/qdrant_client.py`: Handles connection and queries to Qdrant Cloud
- Manages connection pooling, error handling, and retry mechanisms

### Cohere Embedder
- `backend/src/rag_validation/cohere_embedder.py`: Generates embeddings for queries using Cohere API
- Ensures consistency with the embedding model used during indexing
- Includes rate limiting handling and retry mechanisms

### Query Validator
- `backend/src/rag_validation/query_validator.py`: Executes validation queries and collects results
- Implements the validation workflow and metrics collection

### Result Evaluator
- `backend/src/rag_validation/result_evaluator.py`: Evaluates retrieval quality and generates metrics
- Calculates precision, recall, and semantic alignment scores

## Validation Metrics

The system measures:

- **Connection Success Rate**: Percentage of successful connections to Qdrant Cloud
- **Query Response Time**: Time taken to retrieve results (target: <2 seconds)
- **Semantic Alignment**: Relevance of retrieved chunks to the query (target: >80%)
- **Metadata Accuracy**: Correctness of retrieved metadata (target: 100%)
- **Pipeline Stability**: Consistency of results across multiple runs

## Sample Output

After running validation, you'll see output like:

```
Validation Results:
- Connection Success Rate: 99.5% (199/200 successful)
- Average Query Time: 1.2s (target: <2s)
- Semantic Alignment: 84.2% (target: >80%)
- Metadata Accuracy: 100.0% (target: 100%)
- Pipeline Stability: Consistent results across 10 runs
```

## Troubleshooting

### Common Issues

1. **Connection Errors**: Verify QDRANT_HOST and QDRANT_API_KEY in .env file
2. **Cohere Errors**: Check COHERE_API_KEY and rate limits
3. **Slow Queries**: Consider reducing top-k parameter or optimizing network connection
4. **No Results**: Verify collection name and ensure it contains indexed book content

### Environment Setup Verification

Run this command to verify your environment is properly configured:
```bash
cd backend
python -m scripts.validate_retrieval verify-config
```

## API Endpoints

The validation system also exposes API endpoints for programmatic access:

- `GET /api/v1/validate/connection` - Test Qdrant connection
- `POST /api/v1/validate/query` - Validate a single query
- `POST /api/v1/validate/batch` - Run batch validation

For full API documentation, see `backend/docs/api_documentation.md`.

## Testing

Run the test suite to verify all functionality:

```bash
cd backend
python -m pytest tests/ -v
```

This will run all unit and integration tests to ensure the validation pipeline is working correctly.