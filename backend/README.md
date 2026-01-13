# Docusaurus RAG Indexing Backend - Fixed Version

This backend service extracts content from Docusaurus book URLs, generates semantic embeddings using Cohere, and stores them in Qdrant vector database for RAG (Retrieval-Augmented Generation) applications. This is a fixed version that addresses the crashing issue by running as a simple API server without automatically indexing large amounts of data.

## Problem Solved

The original version was crashing because it automatically tried to crawl and index an entire Docusaurus site when started, fetching too much data at once. This version fixes that by:

1. Running as a simple API server without automatic indexing
2. Only performing searches when requested via the API
3. Including proper error handling and rate limiting
4. Using a lightweight server setup with FastAPI

## Features

- Crawls Docusaurus sites to find all content pages
- Extracts clean text content from web pages
- Chunks text with overlap to preserve context
- Generates semantic embeddings using Cohere models
- Stores embeddings and metadata in Qdrant vector database
- Provides search functionality to retrieve relevant content
- FastAPI-based server for the RAG chatbot integration
- Proper API endpoints for frontend communication

## Requirements

- Python 3.8+ (for the server version)
- Cohere API key
- Qdrant vector database (local or cloud)
- FastAPI and uvicorn (included in requirements)

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   # OR if using UV:
   uv pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and Qdrant configuration
   ```

## Usage

### Server Mode (Fixed - No Crashing)
To run the RAG Chatbot API server:
```bash
python server_only.py
# Server will start on http://localhost:8000
```

Or use the provided scripts:
- On Linux/Mac: `./start_server.sh`
- On Windows: `start_server.bat`

### API Endpoints
Once running, the server provides these endpoints:
- `GET /health` - Health check
- `POST /query` - Query the RAG system

### Query Example:
```json
{
  "question": "Your question here",
  "selectedText": "Optional selected text for context",
  "pageContext": "Optional page context"
}
```

### For Indexing (Separate Process)
If you need to index data, run the original main.py separately:
```bash
python main.py "https://your-docusaurus-book.com"
```

## Configuration

The application can be configured using environment variables in the `.env` file:

- `COHERE_API_KEY`: Your Cohere API key
- `QDRANT_URL`: Qdrant cloud instance URL (optional if using local)
- `QDRANT_API_KEY`: Qdrant cloud instance API key
- `QDRANT_HOST`: Local Qdrant host (default: localhost)
- `QDRANT_PORT`: Local Qdrant port (default: 6333)
- `CHUNK_SIZE`: Size of text chunks in characters (default: 1000)
- `CHUNK_OVERLAP`: Overlap between chunks in characters (default: 200)
- `MODEL_NAME`: Cohere embedding model name (default: embed-english-v3.0)
- `RATE_LIMIT_DELAY`: Delay between requests in seconds (default: 1.0)
- `TOP_K_RESULTS`: Number of results to return in search (default: 5)

## Functions

The main.py file contains these key functions:

- `get_all_urls()`: Crawls a Docusaurus site to find all content URLs
- `extract_text_from_url()`: Extracts clean text from a single URL
- `chunk_text()`: Splits text into overlapping chunks
- `embed()`: Generates embeddings using Cohere
- `create_collection()`: Sets up Qdrant collection
- `save_chunk_to_qdrant()`: Stores embeddings in Qdrant
- `search()`: Retrieves relevant content based on query
- `main()`: Orchestrates the entire process

## Architecture

The system follows a pipeline approach:

1. URL Crawling: Discover all pages in a Docusaurus site
2. Content Extraction: Extract clean text from each page
3. Text Chunking: Split content into appropriately sized chunks
4. Embedding Generation: Create semantic vectors using Cohere
5. Vector Storage: Store embeddings in Qdrant with metadata
6. Content Retrieval: Search functionality for RAG applications

## Error Handling and Resilience

- Comprehensive error handling with detailed logging
- Retry logic with exponential backoff for transient failures
- Rate limiting to respect server resources
- Graceful degradation when individual URLs fail
- Memory management for large books

## Performance Monitoring

- Execution time tracking for key functions
- Detailed logging for monitoring and debugging
- Configurable parameters for performance tuning

## Security

- API keys stored in environment variables (not committed)
- Input validation for URLs and search queries
- Rate limiting to prevent abuse