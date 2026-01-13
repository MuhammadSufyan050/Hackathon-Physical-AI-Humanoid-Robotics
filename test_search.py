import os
from dotenv import load_dotenv
import cohere
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Load environment variables
load_dotenv()

# Initialize Cohere client
cohere_api_key = os.getenv("COHERE_API_KEY")
co = cohere.Client(cohere_api_key)

# Initialize Qdrant client
qdrant_url = os.getenv("QDRANT_URL")
qdrant_api_key = os.getenv("QDRANT_API_KEY")
qdrant_host = os.getenv("QDRANT_HOST", "localhost")
qdrant_port = int(os.getenv("QDRANT_PORT", 6333))

if qdrant_url:
    client = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
else:
    client = QdrantClient(host=qdrant_host, port=qdrant_port)

# Test search
query = "What is artificial intelligence?"
print(f"Searching for: {query}")

# Generate embedding for the query using the same method as server_only.py
query_embedding = co.embed(
    texts=[query],
    model="embed-english-v3.0",
    input_type="search_query"  # This is how server_only.py does it
).embeddings[0]

print(f"Query embedding length: {len(query_embedding)}")

# Search in Qdrant
search_results = client.search(
    collection_name="rag_embedding",
    query_vector=query_embedding,
    limit=5,
    with_payload=True
)

print(f"Found {len(search_results)} results:")
for i, hit in enumerate(search_results):
    print(f"Result {i+1}:")
    print(f"  Text: {hit.payload.get('text', '')[:100]}...")
    print(f"  Title: {hit.payload.get('title', '')}")
    print(f"  URL: {hit.payload.get('url', '')}")
    print(f"  Similarity: {hit.score}")
    print()