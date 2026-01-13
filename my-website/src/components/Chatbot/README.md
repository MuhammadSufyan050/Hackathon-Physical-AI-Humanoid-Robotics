# Docusaurus RAG Chatbot Components

This directory contains the React components for the Docusaurus RAG (Retrieval-Augmented Generation) chatbot that integrates with the documentation site.

## Components

### Chatbot.jsx
Main chatbot component that manages the conversation state, handles API communication, and orchestrates the other components.

**Props:**
- `pageContext` (string, optional): URL or identifier of the current page for context

### Message.jsx
Displays individual chat messages, either user questions or AI responses with source references.

**Props:**
- `message` (object): Message object with id, type, content, and timestamp
- `sources` (array, optional): Array of source reference objects

### ChatInput.jsx
Handles user input for questions and displays selected text context.

**Props:**
- `onSubmit` (function): Callback function to handle question submission
- `isLoading` (boolean, optional): Whether the chat is currently processing a request
- `selectedText` (string, optional): Text that the user has selected on the page

## Usage

### In Docusaurus MDX files:
```jsx
import ChatbotDocusaurus from '@site/src/components/ChatbotDocusaurus';

<ChatbotDocusaurus />
```

### Standalone usage:
```jsx
import Chatbot from '@site/src/components/Chatbot/Chatbot';

<Chatbot pageContext={window.location.href} />
```

## API Integration

The chatbot communicates with the backend via the API utilities in `src/utils/api.js`:

- `queryBackend(question, selectedText, pageContext)`: Send a query to the backend
- `queryBackendWithTimeout(question, selectedText, pageContext, timeoutMs)`: Send a query with timeout handling
- `verifyBackendConnection()`: Check if the backend is accessible

## State Management

- Messages are persisted in sessionStorage to maintain conversation across page navigations
- Selected text is tracked using the browser's Selection API
- Loading states are properly managed during API calls
- Error handling provides user feedback for various failure scenarios

## Styling

The components use CSS modules and follow Docusaurus theming by using CSS variables that adapt to the current theme.