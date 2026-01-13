# ADR 003: Text Selection and Context Handling for RAG Queries

## Status
Accepted

## Date
2025-12-24

## Context
The RAG chatbot needs to capture user-selected text on documentation pages and pass it as additional context to the backend retrieval agent. This enables users to ask targeted questions about specific content they're reading, improving the relevance of responses. The system must detect text selection, capture the content, and include it in query requests to the backend.

## Decision
We will implement text selection handling using the browser's Selection API with the following approach:
- Use `window.getSelection()` to get currently selected text
- Add event listeners for 'mouseup' and 'keyup' events to detect selection changes
- Pass selected text as additional context in the query request payload
- Include the selected text in the 'selectedText' field of API requests
- Handle empty selections gracefully when no text is selected

## Alternatives Considered
1. **Manual text input**: Require users to manually copy and paste text. Rejected as it adds friction to the user experience.
2. **Highlight-based selection**: Implement custom highlighting mechanism. Rejected as it would require more complex implementation and reinvent browser functionality.
3. **Right-click context menu**: Add custom context menu option. Rejected as it would be less discoverable and intuitive.
4. **Visual selection tool**: Overlay tool for text selection. Rejected as overly complex for this use case.

## Consequences
### Positive
- Seamless user experience - leverages familiar browser text selection
- No additional UI elements needed for selection
- Works with all existing content without modifications
- Intuitive for users who are familiar with text selection

### Negative
- Selection may be accidentally triggered by users
- Need to handle edge cases like very long selections
- May not work consistently across all browsers
- Requires careful handling to avoid capturing unintended selections

## References
- specs/1-docusaurus-rag-integration/plan.md
- specs/1-docusaurus-rag-integration/research.md
- specs/1-docusaurus-rag-integration/data-model.md