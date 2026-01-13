# Data Model: Docusaurus RAG Chatbot Integration

## Entities

### Question
- **Description**: Natural language query submitted by the user
- **Fields**:
  - `id` (string): Unique identifier for the question
  - `text` (string): The actual question text
  - `selectedText` (string, optional): Text selected by user on the current page
  - `timestamp` (date): When the question was submitted
  - `pageContext` (string, optional): URL or identifier of the current page

### Response
- **Description**: Answer returned by the retrieval agent with source references
- **Fields**:
  - `id` (string): Unique identifier for the response
  - `questionId` (string): Reference to the associated question
  - `text` (string): The answer text
  - `sources` (array of SourceReference): List of sources used in the response
  - `timestamp` (date): When the response was received
  - `status` (string): Success, error, or timeout

### SourceReference
- **Description**: Metadata indicating where information in the response originated
- **Fields**:
  - `id` (string): Unique identifier for the source
  - `title` (string): Title of the source document/page
  - `url` (string): URL to the source document
  - `excerpt` (string): Snippet of text from the source
  - `confidence` (number): Confidence score for the source relevance

### ChatSession
- **Description**: Stateful interaction context that maintains conversation history
- **Fields**:
  - `id` (string): Unique identifier for the session
  - `userId` (string, optional): User identifier (anonymous for now)
  - `messages` (array of Message): History of questions and responses
  - `currentPage` (string): Current page context
  - `createdAt` (date): When the session was created
  - `lastActivityAt` (date): When the session was last used

### Message
- **Description**: Base entity for both questions and responses in a chat session
- **Fields**:
  - `id` (string): Unique identifier for the message
  - `sessionId` (string): Reference to the chat session
  - `type` (string): "question" or "response"
  - `content` (string): The message content
  - `timestamp` (date): When the message was created
  - `metadata` (object, optional): Additional metadata based on type

## State Transitions

### ChatSession States
1. **New**: Session created but no messages exchanged
2. **Active**: Session has exchanged messages, less than 30 minutes since last activity
3. **Inactive**: Session has not been active for more than 30 minutes

### Message States
1. **Pending**: Question sent to backend, waiting for response
2. **Processing**: Backend is processing the query
3. **Complete**: Response received and displayed
4. **Error**: Error occurred during processing

## Validation Rules

### Question Validation
- `text` must be 1-1000 characters
- `selectedText` must be 0-5000 characters if provided
- Must have either `text` or `selectedText`

### Response Validation
- `text` must be provided and non-empty
- `sources` array must contain at least one source if content was retrieved
- `status` must be one of: "success", "error", "timeout"

### SourceReference Validation
- `title` and `url` must be provided
- `confidence` must be between 0 and 1
- `excerpt` should be less than 1000 characters

## API Payloads

### Query Request
```json
{
  "question": "string",
  "selectedText": "string (optional)",
  "pageContext": "string (optional)"
}
```

### Query Response
```json
{
  "id": "string",
  "questionId": "string",
  "answer": "string",
  "sources": [
    {
      "title": "string",
      "url": "string",
      "excerpt": "string",
      "confidence": "number"
    }
  ],
  "status": "success|error|timeout"
}
```