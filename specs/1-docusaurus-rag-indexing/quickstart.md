# Quickstart: Docusaurus Book Content for RAG Indexing

## Prerequisites

- Python 3.11 or higher
- pip package manager
- Cohere API key
- Qdrant vector database (local or cloud instance)

## Setup

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-name>
```

### 2. Create Backend Directory and Setup UV Package
```bash
mkdir backend
cd backend
uv init  # if uv is available, otherwise use pip
```

Or if uv is not available:
```bash
mkdir backend
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install cohere qdrant-client requests beautifulsoup4 python-dotenv
```

### 4. Environment Configuration
Create a `.env` file in the backend directory:
```env
COHERE_API_KEY=your_cohere_api_key_here
QDRANT_URL=your_qdrant_url_here  # Optional, for cloud instance
QDRANT_API_KEY=your_qdrant_api_key_here  # Optional, for cloud instance
QDRANT_HOST=localhost  # For local instance
QDRANT_PORT=6333  # Default Qdrant port
```

## Usage

### 1. Run the Indexing Process
```bash
cd backend
python main.py
```

The main script will:
1. Fetch all URLs from the specified Docusaurus book
2. Extract text content from each URL
3. Chunk the text appropriately
4. Generate embeddings using Cohere
5. Create the "rag_embedding" collection in Qdrant
6. Save all chunks to Qdrant with metadata

### 2. Configure Your Target Book
Modify the base URL in the main function to point to your target Docusaurus book:
```python
if __name__ == "__main__":
    base_url = "https://hackathon-physical-ai-humanoid-robo-ten.vercel.app/"  # Your Docusaurus book URL
    main(base_url)
```

## Configuration Options

### Text Chunking
- `CHUNK_SIZE`: Maximum characters per chunk (default: 1000)
- `CHUNK_OVERLAP`: Overlap between chunks in characters (default: 200)

### Embedding Model
- Modify the `model` parameter in the embed function to use different Cohere models
- Current default: "embed-english-v3.0"

### Qdrant Collection
- Collection name: "rag_embedding" (hardcoded)
- Vector size: 1024 (for Cohere embeddings)

## Running with Different Books

To index a different Docusaurus book:

1. Update the base URL in the main function
2. Ensure the site allows scraping (check robots.txt)
3. Run the script again

## Troubleshooting

### Common Issues

1. **API Rate Limits**: If you encounter rate limits, implement additional delays between API calls
2. **Connection Errors**: Verify Qdrant is running and accessible
3. **Invalid URLs**: Ensure the target Docusaurus site is accessible and allows scraping

### Verification

To verify the indexing worked:
1. Check that the "rag_embedding" collection exists in Qdrant
2. Verify the number of points in the collection matches expected chunks
3. Test retrieval with a sample query