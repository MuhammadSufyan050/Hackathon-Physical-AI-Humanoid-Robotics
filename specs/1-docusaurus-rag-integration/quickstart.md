# Quickstart: Docusaurus RAG Chatbot Integration

## Prerequisites

Before starting the implementation, ensure you have:

- Node.js 18+ installed
- Python 3.11+ installed
- Access to OpenAI API key
- Access to Cohere API key
- Qdrant vector database instance (local or remote)

## Environment Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <repository-name>
   ```

2. **Set up backend environment**
   ```bash
   cd backend/
   pip install -r requirements.txt
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. **Set up frontend environment**
   ```bash
   cd my-website/
   npm install
   ```

## Running the Backend

1. **Start the Qdrant vector database** (if using local instance)
   ```bash
   # Using Docker
   docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
   ```

2. **Run the backend server**
   ```bash
   cd backend/
   python main.py
   ```

## Running the Frontend

1. **Start the Docusaurus development server**
   ```bash
   cd my-website/
   npm start
   ```

## Implementation Steps

### Step 1: Create the Chatbot Component

Create the main chatbot component in `src/components/Chatbot/Chatbot.jsx`:

```jsx
import React, { useState } from 'react';
import ChatInput from './ChatInput';
import MessageList from './MessageList';
import './Chatbot.css';

const Chatbot = ({ pageContext }) => {
  const [messages, setMessages] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (question, selectedText) => {
    // Add user message to UI immediately
    const userMessage = {
      id: Date.now().toString(),
      type: 'question',
      content: question,
      selectedText,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Call backend API
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question,
          selectedText,
          pageContext
        })
      });

      const data = await response.json();

      const botMessage = {
        id: Date.now().toString(),
        type: 'response',
        content: data.answer,
        sources: data.sources,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      const errorMessage = {
        id: Date.now().toString(),
        type: 'response',
        content: 'Sorry, I encountered an error processing your request.',
        error: true,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="chatbot-container">
      <div className="chatbot-header">
        <h3>Book Assistant</h3>
      </div>
      <MessageList messages={messages} />
      <ChatInput
        onSubmit={handleSubmit}
        isLoading={isLoading}
      />
    </div>
  );
};

export default Chatbot;
```

### Step 2: Create API Utility Functions

Create `src/utils/api.js`:

```javascript
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export const queryBackend = async (question, selectedText = '', pageContext = '') => {
  try {
    const response = await fetch(`${API_BASE_URL}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        question,
        selectedText,
        pageContext
      })
    });

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
};
```

### Step 3: Add Text Selection Utility

Create `src/utils/textSelection.js`:

```javascript
export const getSelectedText = () => {
  const selection = window.getSelection();
  return selection.toString().trim();
};

export const addSelectionListener = (callback) => {
  const handleSelection = () => {
    const selectedText = getSelectedText();
    callback(selectedText);
  };

  document.addEventListener('mouseup', handleSelection);
  document.addEventListener('keyup', handleSelection);

  // Return cleanup function
  return () => {
    document.removeEventListener('mouseup', handleSelection);
    document.removeEventListener('keyup', handleSelection);
  };
};
```

### Step 4: Integrate into Docusaurus Pages

To add the chatbot to a Docusaurus page, import and use the component:

```jsx
import Chatbot from '../components/Chatbot/Chatbot';

function MyPage() {
  return (
    <div>
      <main>
        {/* Your page content */}
      </main>
      <aside>
        <Chatbot pageContext={typeof window !== 'undefined' ? window.location.href : ''} />
      </aside>
    </div>
  );
}
```

## Testing the Integration

1. **Start both backend and frontend servers**
2. **Navigate to a documentation page**
3. **Test the chatbot by asking questions about the content**
4. **Verify that selected text is captured and sent with queries**
5. **Check that responses include proper source references**

## API Endpoints

The backend provides the following endpoints for the chatbot:

- `POST /query` - Submit a question and receive a response with sources
- `GET /health` - Check backend health status

## Troubleshooting

- **Backend not responding**: Ensure the backend server is running and accessible
- **CORS errors**: Check that the backend allows requests from the frontend origin
- **API key errors**: Verify that all required API keys are properly configured
- **Empty responses**: Check that the vector database has been properly indexed with content