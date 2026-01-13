# Book Q&A Retrieval Agent

A retrieval-enabled agent for book Q&A using OpenAI Agents SDK with Qdrant vector database integration. The agent accepts user questions via CLI, generates Cohere embeddings for semantic search, retrieves relevant content from Qdrant, and generates grounded answers with source references.

## Features

- Semantic search of book content using vector embeddings
- Integration with Qdrant vector database
- Cohere embeddings for query and content representation
- OpenAI Agents SDK for intelligent question answering
- Source attribution for all answers
- Graceful handling of out-of-scope questions

## Prerequisites

- Python 3.11+
- OpenAI API key
- Cohere API key
- Qdrant Cloud endpoint and API key
- Book content indexed in Qdrant collection

## Setup

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill in your API keys
4. Run the agent: `python -m src.cli.main`

## Usage

```bash
# Interactive mode
python -m src.cli.main

# Single query
python -m src.cli.main --query "Your question here"
```

## Architecture

The agent follows a Retrieval-Augmented Generation (RAG) pattern:
1. User asks a question via CLI
2. Agent generates embeddings for the question using Cohere
3. Agent queries Qdrant for relevant content based on embeddings
4. Agent uses retrieved content as context to generate a grounded response
5. Agent returns response with source metadata indicating where information came from