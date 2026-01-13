# ADR 002: Frontend Component Architecture for Docusaurus RAG Chatbot

## Status
Accepted

## Date
2025-12-24

## Context
The Docusaurus documentation site needs to embed a chatbot UI component that can capture user queries and selected text, communicate with the backend retrieval agent, and display grounded responses with source references. The solution must follow Docusaurus conventions and integrate seamlessly with the existing documentation site structure.

## Decision
We will implement the chatbot as React components that can be embedded in Docusaurus pages with the following architecture:
- **Chatbot.jsx**: Main container component managing state and communication
- **Message.jsx**: Individual message display component for questions and responses
- **ChatInput.jsx**: Input component with text selection handling capabilities
- **utils/api.js**: API communication functions
- **utils/textSelection.js**: Text selection utilities using browser Selection API

## Alternatives Considered
1. **Standalone widget**: Self-contained JavaScript widget loaded via script tag. Rejected as it would be harder to integrate with React/Docusaurus state management.
2. **Full page application**: Separate application instead of embedded component. Rejected as it would break the seamless documentation experience.
3. **IFrame embedding**: Isolated component in iframe. Rejected due to complexity in communication and styling consistency issues.
4. **Native Docusaurus plugin**: Deep integration at the Docusaurus level. Rejected as overly complex for this feature scope.

## Consequences
### Positive
- Seamless integration with existing Docusaurus structure
- Consistent styling and user experience
- Proper state management within React ecosystem
- Easy to customize and extend
- Follows Docusaurus conventions

### Negative
- Requires React knowledge for future modifications
- Adds to the bundle size of documentation pages
- Potential complexity in managing component lifecycle with page navigation

## References
- specs/1-docusaurus-rag-integration/plan.md
- specs/1-docusaurus-rag-integration/research.md
- specs/1-docusaurus-rag-integration/data-model.md