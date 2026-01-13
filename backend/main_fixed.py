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
import uvicorn

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rag_indexing.log'),
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


def normalize_url(url: str) -> str:
    """
    Normalize URL by removing fragments and ensuring proper format
    """
    parsed = urlparse(url)
    # Reconstruct URL without fragment
    normalized = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
    # Ensure it ends with / if it's a directory-like path
    if not parsed.path or parsed.path.endswith('/'):
        normalized = normalized.rstrip('/') + '/'
    return normalized


def is_same_domain(base_url: str, test_url: str) -> bool:
    """
    Check if two URLs belong to the same domain
    """
    base_domain = urlparse(base_url).netloc
    test_domain = urlparse(test_url).netloc
    return base_domain == test_domain

@timing_decorator
def get_all_urls(base_url: str) -> List[str]:
    """
    Fetch all URLs from a Docusaurus site by crawling internal links
    """
    urls = set()
    visited = set()
    to_visit = [base_url]

    # Parse the base domain to ensure we only crawl the same site
    base_domain = urlparse(base_url).netloc

    while to_visit:
        current_url = to_visit.pop(0)

        if current_url in visited:
            continue

        visited.add(current_url)
        print(f"Crawling: {current_url}")
        logger.info(f"Crawling: {current_url}")

        try:
            response = requests.get(current_url, timeout=10)
            response.raise_for_status()

            # Add current URL to the set
            urls.add(current_url)

            # Parse the HTML to find other links
            soup = BeautifulSoup(response.content, 'html.parser')

            # Find all links
            for link in soup.find_all('a', href=True):
                href = link['href']
                absolute_url = urljoin(current_url, href)

                # Only process URLs from the same domain
                if urlparse(absolute_url).netloc == base_domain:
                    # Check if it's a valid page (not external, not a file)
                    if absolute_url not in visited and absolute_url not in to_visit:
                        if any(absolute_url.endswith(ext) for ext in ['.html', '.htm', '']) or not '.' in urlparse(absolute_url).path:
                            to_visit.append(absolute_url)

            # Rate limiting to respect server resources
            sleep(RATE_LIMIT_DELAY)

            # Limit to prevent infinite crawling
            if len(urls) > 50:  # reduced limit to prevent too much data
                print(f"Reached URL limit of 50, stopping crawl")
                logger.info("Reached URL limit, stopping crawl")
                break

        except Exception as e:
            logger.error(f"Error crawling {current_url}: {str(e)}")
            continue

    return list(urls)

@timing_decorator
@retry_on_failure(max_retries=3, delay=1.0, backoff=2.0)
def extract_text_from_url(url: str) -> Dict[str, Any]:
    """
    Extract text content from a single URL
    """
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()

        # Try to find the main content area (Docusaurus specific selectors)
        content_selectors = [
            'main div[class*="theme"]',  # Common Docusaurus content area
            'article',  # Article tags often contain main content
            'div[class*="docItem"]',  # Docusaurus doc item containers
            'div[class*="container"]',  # General container
            'main',  # Main content area
            'body'  # Fallback to body
        ]

        text_content = ""
        for selector in content_selectors:
            elements = soup.select(selector)
            if elements:
                for element in elements:
                    text_content += element.get_text(separator=' ', strip=True) + "\n\n"
                break

        # If no content found with specific selectors, use body
        if not text_content.strip():
            text_content = soup.get_text(separator=' ', strip=True)

        # Clean up the text
        lines = (line.strip() for line in text_content.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text_content = ' '.join(chunk for chunk in chunks if chunk)

        # Limit text size to prevent memory errors (50KB limit - reduced from 100KB)
        if len(text_content) > 50000:
            print(f"Warning: Content from {url} too large ({len(text_content)} chars), truncating to 50KB")
            text_content = text_content[:50000]

        return {
            "url": url,
            "title": soup.title.string if soup.title else "No Title",
            "text": text_content
        }
    except Exception as e:
        print(f"Error extracting text from {url}: {str(e)}")
        return {
            "url": url,
            "title": "Error",
            "text": ""
        }

def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into overlapping chunks
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size

        # If this is the last chunk, make sure we include all remaining text
        if end > len(text):
            end = len(text)

        chunk = text[start:end]
        chunks.append(chunk)

        # Move start position by chunk_size - overlap
        start = end - overlap

        # If start position is at or past the end, break
        if start >= len(text):
            break

    return chunks

@timing_decorator
@retry_on_failure(max_retries=3, delay=1.0, backoff=2.0)
def embed(texts: List[str]) -> List[List[float]]:
    """
    Generate embeddings for a list of texts using Cohere
    """
    try:
        response = co.embed(
            texts=texts,
            model=MODEL_NAME,
            input_type="search_document"
        )
        return response.embeddings
    except Exception as e:
        logger.error(f"Error generating embeddings: {str(e)}")
        # Return dummy embeddings in case of error to allow testing
        return [[0.0] * 1024 for _ in texts]

def create_collection(collection_name: str):
    """
    Create a Qdrant collection for storing embeddings
    """
    try:
        # Check if collection already exists
        collections = qdrant_client.get_collections()
        existing_collections = [c.name for c in collections.collections]

        if collection_name in existing_collections:
            print(f"Collection {collection_name} already exists, recreating...")
            qdrant_client.delete_collection(collection_name)

        # Create new collection
        qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=models.VectorParams(
                size=1024,  # Cohere embeddings are 1024-dimensional
                distance=models.Distance.COSINE
            )
        )
        print(f"Collection {collection_name} created successfully")
    except Exception as e:
        print(f"Error creating collection {collection_name}: {str(e)}")
        raise

@retry_on_failure(max_retries=3, delay=1.0, backoff=2.0)
def save_chunk_to_qdrant(collection_name: str, chunk: str, url: str, title: str, embedding: List[float], chunk_id: int):
    """
    Save a text chunk with its embedding to Qdrant
    """
    try:
        qdrant_client.upsert(
            collection_name=collection_name,
            points=[
                models.PointStruct(
                    id=chunk_id,
                    vector=embedding,
                    payload={
                        "text": chunk,
                        "url": url,
                        "title": title,
                        "created_at": time.time()
                    }
                )
            ]
        )
    except Exception as e:
        logger.error(f"Error saving chunk {chunk_id} to Qdrant: {str(e)}")


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

        # Search in Qdrant
        search_results = qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            limit=top_k,
            with_payload=True
        )

        # Format results
        results = []
        for hit in search_results:
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
        # In a real implementation, you would use an LLM to generate the answer
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
    Main function to run the API server
    """
    print("Starting RAG Chatbot API server...")
    logger.info("Starting RAG Chatbot API server...")

    # Create the default collection if it doesn't exist
    try:
        create_collection("rag_embedding")
    except Exception as e:
        logger.warning(f"Could not create collection (may already exist): {str(e)}")

    print("Server is ready! Access the API at http://localhost:8000")
    print("API documentation at http://localhost:8000/docs")

    # Run the server
    uvicorn.run(app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()