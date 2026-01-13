# ADR 001: API Communication Strategy for Docusaurus RAG Chatbot

## Status
Accepted

## Date
2025-12-24

## Context
The Docusaurus RAG chatbot frontend needs to communicate with the backend retrieval agent to process user queries and return grounded responses with source metadata. The system must support passing user queries, selected text context, and page context from the frontend to the backend, and return responses with proper source attribution.

## Decision
We will use a REST API approach for frontend-backend communication with the following characteristics:
- HTTP POST requests to `/query` endpoint
- JSON request/response format
- Standard HTTP status codes for error handling
- Request payload containing question, selected text, and page context
- Response payload containing answer and source references

## Alternatives Considered
1. **Direct database access**: Bypass the backend API and access the vector database directly. Rejected because it would bypass backend logic, security measures, and business rules implemented in the backend.
2. **WebSocket connection**: Real-time bidirectional communication. Rejected as overly complex for the request-response pattern required for this use case.
3. **Server-Sent Events**: Unidirectional server-to-client communication. Not suitable for the request-response pattern needed.
4. **GraphQL API**: More flexible query language. Rejected as unnecessary complexity for this specific use case with well-defined request/response patterns.

## Consequences
### Positive
- Simple request-response pattern matches the use case requirements
- Standard HTTP protocols with well-understood tooling and debugging
- Easy to implement and maintain
- Good compatibility with existing backend infrastructure
- Clear separation of concerns between frontend and backend

### Negative
- Potential latency from HTTP request overhead
- Less efficient than persistent connections for frequent interactions
- Requires proper error handling for network failures

## References
- specs/1-docusaurus-rag-integration/plan.md
- specs/1-docusaurus-rag-integration/research.md
- specs/1-docusaurus-rag-integration/contracts/api-contract.md