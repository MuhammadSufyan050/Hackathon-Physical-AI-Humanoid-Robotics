# Research: Docusaurus RAG Chatbot Integration

## Technical Architecture Overview

### Backend Components
- **Location**: `backend/main.py`
- **Functionality**: RAG indexing and search with Qdrant vector database
- **Embeddings**: Cohere's embed-english-v3.0 model
- **API**: OpenAI GPT-4 Turbo for answer generation
- **Features**: Crawls Docusaurus sites, indexes content, performs semantic search

### Frontend Components
- **Framework**: Docusaurus 3.9.2 (React-based)
- **Structure**: Standard Docusaurus with custom components
- **Location**: `my-website/` directory
- **Configuration**: `docusaurus.config.js` with custom title

### Agent Implementation
- **Location**: `src/agents/book_qna_agent.py`
- **Technology**: OpenAI Assistants API
- **Integration**: Qdrant for retrieval with source attribution
- **Features**: RAG pattern, connection validation

## Decision: API Communication Method

### Rationale
The frontend chatbot will communicate with the backend retrieval agent via REST API endpoints. The backend already has the necessary functionality implemented in `backend/main.py`.

### Alternatives Considered
1. **Direct database access**: Would bypass backend logic and security
2. **WebSocket connection**: More complex than needed for initial implementation
3. **Server-Sent Events**: Not necessary for request-response pattern

## Decision: Component Structure

### Rationale
The chatbot will be implemented as React components that can be embedded in Docusaurus pages. This follows Docusaurus conventions and allows for easy integration.

### Components to Implement
1. **Chatbot.jsx**: Main container component
2. **Message.jsx**: Individual message display
3. **ChatInput.jsx**: Input with text selection handling
4. **utils/api.js**: API communication functions
5. **utils/textSelection.js**: Text selection utilities

## Decision: Text Selection Handling

### Rationale
The chatbot needs to capture user-selected text to provide context for queries. This will be implemented using the browser's Selection API to detect and capture selected text.

### Implementation Approach
- Use `window.getSelection()` to get currently selected text
- Add event listeners for selection changes
- Pass selected text as additional context to the backend query

## Decision: Error Handling Strategy

### Rationale
The system must handle backend failures gracefully to provide a good user experience.

### Implementation
- Implement timeout handling for API calls
- Provide user feedback when backend is unavailable
- Fallback UI states for error conditions
- Connection validation before sending queries

## Decision: Source Attribution Display

### Rationale
The chatbot responses must include source references as required by the constitution to ensure grounded responses.

### Implementation
- Parse source metadata from backend responses
- Display source references alongside answers
- Provide links to original content when possible