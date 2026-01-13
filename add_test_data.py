import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models
import cohere

# Load environment variables
load_dotenv()

# Initialize Cohere client
cohere_api_key = os.getenv("COHERE_API_KEY")
if not cohere_api_key:
    raise ValueError("COHERE_API_KEY environment variable is required")

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

# Create collection if it doesn't exist
try:
    client.get_collection("rag_embedding")
    print("Collection 'rag_embedding' exists, deleting and recreating...")
    client.delete_collection("rag_embedding")
except:
    print("Collection doesn't exist, creating new one...")

client.create_collection(
    collection_name="rag_embedding",
    vectors_config=models.VectorParams(
        size=1024,  # Cohere embeddings are 1024-dimensional
        distance=models.Distance.COSINE
    )
)

# Test documents to add
test_documents = [
    {
        "text": "This is a test document about artificial intelligence and machine learning. AI is a fascinating field that involves creating systems that can perform tasks typically requiring human intelligence.",
        "url": "test://document1",
        "title": "Introduction to AI"
    },
    {
        "text": "Machine learning is a subset of artificial intelligence that focuses on algorithms that can learn from data. Common ML techniques include supervised learning, unsupervised learning, and reinforcement learning.",
        "url": "test://document2",
        "title": "Machine Learning Basics"
    },
    {
        "text": "Natural language processing (NLP) is a field of AI that focuses on the interaction between computers and humans through natural language. NLP techniques are used in chatbots, translation, and text analysis.",
        "url": "test://document3",
        "title": "Natural Language Processing"
    },
    {
        "text": "Vector databases like Qdrant store embeddings that represent the semantic meaning of text. These embeddings allow for semantic search and retrieval of relevant information.",
        "url": "test://document4",
        "title": "Vector Databases"
    },
    {
        "text": "Retrieval Augmented Generation (RAG) combines information retrieval with generative models to provide more accurate and contextually relevant responses to user queries.",
        "url": "test://document5",
        "title": "Retrieval Augmented Generation"
    }
]

# Add documents to Qdrant
for i, doc in enumerate(test_documents):
    # Generate embedding for the text
    embedding = co.embed(
        texts=[doc["text"]],
        model="embed-english-v3.0",
        input_type="search_document"
    ).embeddings[0]

    # Add to Qdrant
    client.upsert(
        collection_name="rag_embedding",
        points=[
            models.PointStruct(
                id=i,
                vector=embedding,
                payload={
                    "text": doc["text"],
                    "url": doc["url"],
                    "title": doc["title"],
                    "created_at": "2025-12-25"
                }
            )
        ]
    )
    print(f"Added document {i+1}: {doc['title']}")

print(f"Successfully added {len(test_documents)} test documents to Qdrant collection 'rag_embedding'")