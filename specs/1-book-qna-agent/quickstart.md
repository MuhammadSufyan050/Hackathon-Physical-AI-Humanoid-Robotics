# Quickstart Guide: Book Q&A Retrieval Agent

## Overview
This guide provides instructions for setting up and running the retrieval-enabled agent for book Q&A.

## Prerequisites
- Python 3.11 or higher
- OpenAI API key
- Cohere API key
- Qdrant Cloud endpoint and API key
- Book content indexed in Qdrant collection

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
pip install -r requirements.txt
```

### 4. Configure Environment Variables
Create a `.env` file in the project root with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key_here
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_URL=your_qdrant_cloud_url_here
QDRANT_API_KEY=your_qdrant_api_key_here
QDRANT_COLLECTION_NAME=your_collection_name_here
```

## Usage

### Running the CLI Agent
```bash
python -m src.cli.main
```

This will start an interactive session where you can ask questions about the book content:

```
$ python -m src.cli.main
Welcome to the Book Q&A Agent!
Ask your questions about the book content (type 'quit' to exit):

> What is the main concept of Chapter 1?
The main concept of Chapter 1 is [answer based on retrieved content with source references].

> How does the author explain neural networks?
Based on the book content, neural networks are explained as [answer with source metadata].

> quit
Goodbye!
```

### Running a Single Query
```bash
python -m src.cli.main --query "Your question here"
```

## Configuration Options

### Environment Variables
- `OPENAI_API_KEY`: API key for OpenAI services
- `COHERE_API_KEY`: API key for Cohere embedding services
- `QDRANT_URL`: URL for Qdrant Cloud instance
- `QDRANT_API_KEY`: API key for Qdrant authentication
- `QDRANT_COLLECTION_NAME`: Name of the collection containing book content
- `EMBEDDING_MODEL`: Cohere model to use for embeddings (default: embed-multilingual-v3.0)
- `TOP_K_RESULTS`: Number of results to retrieve (default: 5)
- `MIN_SCORE_THRESHOLD`: Minimum relevance score (default: 0.5)

## Development

### Running Tests
```bash
pytest tests/
```

### Adding New Features
1. Update the specification in `specs/1-book-qna-agent/spec.md`
2. Update the implementation plan if needed
3. Add new tasks to `specs/1-book-qna-agent/tasks.md`
4. Implement the feature following the task breakdown

## Troubleshooting

### Common Issues

1. **Connection errors to Qdrant**: Verify your QDRANT_URL and QDRANT_API_KEY are correct
2. **Authentication errors**: Check that all API keys are properly set in the .env file
3. **No results returned**: Ensure the book content is properly indexed in Qdrant
4. **Slow responses**: Check your internet connection and API key rate limits

### Debugging
Enable debug logging by setting the environment variable:
```bash
export LOG_LEVEL=DEBUG
```

## Architecture Overview

The agent follows a Retrieval-Augmented Generation (RAG) pattern:
1. User asks a question via CLI
2. Agent generates embeddings for the question using Cohere
3. Agent queries Qdrant for relevant content based on embeddings
4. Agent uses retrieved content as context to generate a grounded response
5. Agent returns response with source metadata indicating where information came from