import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import cohere
from qdrant_client import QdrantClient
from qdrant_client.http import models
from dotenv import load_dotenv
import time
import logging
from typing import List, Dict, Any
import re
from time import sleep
import functools
import random
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rag_server.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Constants
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))  # characters
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "200"))  # characters
MODEL_NAME = os.getenv("MODEL_NAME", "embed-english-v3.0")
RATE_LIMIT_DELAY = float(os.getenv("RATE_LIMIT_DELAY", "1.0"))  # seconds between requests to respect server resources
TOP_K_RESULTS = int(os.getenv("TOP_K_RESULTS", "5"))  # number of results to return in search

# Initialize Cohere client
cohere_api_key = os.getenv("COHERE_API_KEY")
if not cohere_api_key:
    raise ValueError("COHERE_API_KEY environment variable is required")

try:
    co = cohere.Client(cohere_api_key)
    # Validate Cohere connection by making a simple API call (using embed as a test)
    test_response = co.embed(texts=["test"], model=MODEL_NAME, input_type="search_document")
    logger.info("Successfully connected to Cohere API")
except Exception as e:
    logger.error(f"Failed to connect to Cohere API: {str(e)}")
    raise

# Initialize Qdrant client
qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
qdrant_host = os.getenv("QDRANT_HOST", "localhost")
qdrant_port = int(os.getenv("QDRANT_PORT", 6333))

if qdrant_url:
    qdrant_client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
else:
    qdrant_client = QdrantClient(host=qdrant_host, port=qdrant_port)

# Validate Qdrant connection
try:
    qdrant_client.get_collections()
    logger.info("Successfully connected to Qdrant")
except Exception as e:
    logger.error(f"Failed to connect to Qdrant: {str(e)}")
    raise


def timing_decorator(func):
    """
    Decorator to measure execution time of functions
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"{func.__name__} executed in {execution_time:.2f} seconds")
        return result
    return wrapper


def retry_on_failure(max_retries: int = 3, delay: float = 1.0, backoff: float = 2.0):
    """
    Decorator to retry functions on failure
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            retries = 0
            current_delay = delay

            while retries < max_retries:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    retries += 1
                    if retries >= max_retries:
                        logger.error(f"Function {func.__name__} failed after {max_retries} attempts: {str(e)}")
                        raise

                    logger.warning(f"Attempt {retries} failed for {func.__name__}: {str(e)}. Retrying in {current_delay}s...")
                    sleep(current_delay)
                    current_delay *= backoff
                    # Add some jitter to avoid thundering herd problem
                    current_delay += random.uniform(0, 1)

        return wrapper
    return decorator


def is_valid_url(url: str) -> bool:
    """
    Validate if a string is a properly formatted URL
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


@timing_decorator
@retry_on_failure(max_retries=3, delay=1.0, backoff=2.0)
def search(query: str, collection_name: str = "rag_embedding", top_k: int = TOP_K_RESULTS) -> List[Dict[str, Any]]:
    """
    Find relevant content in Qdrant based on query
    """
    try:
        # Generate embedding for the query
        query_embedding = co.embed(
            texts=[query],
            model=MODEL_NAME,
            input_type="search_query"
        ).embeddings[0]

        # Search in Qdrant using the newer API
        search_results = qdrant_client.query_points(
            collection_name=collection_name,
            query=query_embedding,
            limit=top_k,
            with_payload=True
        )

        # Format results
        results = []
        for hit in search_results.points:
            result = {
                "text": hit.payload.get("text", ""),
                "url": hit.payload.get("url", ""),
                "title": hit.payload.get("title", ""),
                "similarity_score": hit.score,
                "metadata": {
                    "created_at": hit.payload.get("created_at", ""),
                }
            }
            results.append(result)

        logger.info(f"Search completed for query: '{query[:50]}...', found {len(results)} results")
        return results
    except Exception as e:
        logger.error(f"Error during search: {str(e)}")
        return []


# FastAPI setup for the server
app = FastAPI(title="RAG Chatbot API", description="API for the Docusaurus RAG Chatbot")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    question: str
    selectedText: str = ""
    pageContext: str = ""

class QueryResponse(BaseModel):
    id: str
    questionId: str
    answer: str
    sources: List[Dict[str, Any]]
    status: str

class HealthResponse(BaseModel):
    status: str
    timestamp: str

@app.get("/health", response_model=HealthResponse)
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": time.strftime('%Y-%m-%d %H:%M:%S')
    }

@app.post("/query", response_model=QueryResponse)
def query_endpoint(request: QueryRequest):
    """Query endpoint for the RAG system"""
    try:
        # Combine question with selected text if provided
        search_query = request.question
        if request.selectedText:
            search_query = f"{request.question} Context: {request.selectedText}"

        # Perform search
        results = search(search_query)

        # Format sources
        sources = []
        for result in results:
            source = {
                "title": result["title"],
                "url": result["url"],
                "excerpt": result["text"][:200] + "..." if len(result["text"]) > 200 else result["text"],
                "confidence": result["similarity_score"]
            }
            sources.append(source)

        # Generate a simple response based on search results
        if results:
            answer = f"I found {len(results)} relevant sources. Here's information based on the documentation:\n\n{results[0]['text'][:500]}..."
        else:
            answer = "I couldn't find relevant information in the documentation for your query."

        return QueryResponse(
            id=str(int(time.time() * 1000)),
            questionId=str(int(time.time() * 1000)),
            answer=answer,
            sources=sources,
            status="success"
        )
    except Exception as e:
        logger.error(f"Error processing query: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

def main():
    """
    Main function to run the API server without auto-indexing
    """
    print("Starting RAG Chatbot API server...")
    logger.info("Starting RAG Chatbot API server...")

    print("Server is ready! Access the API at http://localhost:8001")
    print("API documentation at http://localhost:8001/docs")

    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8001)

if __name__ == "__main__":
    main()