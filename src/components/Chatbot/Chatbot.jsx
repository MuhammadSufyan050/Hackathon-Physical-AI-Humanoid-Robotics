import React, { useState, useEffect, useCallback } from 'react';
import Message from './Message';
import ChatInput from './ChatInput';
import { queryBackendWithTimeout, verifyBackendConnection } from '../../utils/api';
import { getSelectedText, addSelectionListener } from '../../utils/textSelection';
import './Chatbot.css';

/**
 * Main Chatbot component that integrates all functionality
 * Handles state management, API communication, and UI rendering
 */
const Chatbot = ({ pageContext = '' }) => {
  // Initialize messages from session storage to preserve conversation across page navigations
  const [messages, setMessages] = useState(() => {
    if (typeof window !== 'undefined') {
      const savedMessages = sessionStorage.getItem('chatbot-messages');
      return savedMessages ? JSON.parse(savedMessages) : [];
    }
    return [];
  });
  const [isLoading, setIsLoading] = useState(false);
  const [selectedText, setSelectedText] = useState('');
  const [backendConnected, setBackendConnected] = useState(false);

  // Initialize and verify backend connection
  useEffect(() => {
    const initializeConnection = async () => {
      const connected = await verifyBackendConnection();
      setBackendConnected(connected);
    };

    initializeConnection();
  }, []);

  // Set up text selection listener
  useEffect(() => {
    const cleanup = addSelectionListener(setSelectedText);
    return cleanup;
  }, []);

  const handleSubmit = useCallback(async (question, selectedTextContext) => {
    if (!question.trim() && !selectedTextContext.trim()) return;

    const startTime = Date.now();

    // Add user message to UI immediately
    const userMessage = {
      id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type: 'question',
      content: question,
      timestamp: new Date().toISOString(),
    };

    const updatedMessages = [...messages, userMessage];
    setMessages(updatedMessages);
    // Save messages to session storage
    if (typeof window !== 'undefined') {
      sessionStorage.setItem('chatbot-messages', JSON.stringify(updatedMessages));
    }
    setIsLoading(true);

    try {
      // Call backend API with timeout
      const response = await queryBackendWithTimeout(
        question,
        selectedTextContext,
        pageContext
      );

      const botMessage = {
        id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        type: 'response',
        content: response.answer,
        sources: response.sources || [],
        timestamp: new Date().toISOString(),
      };

      const finalMessages = [...updatedMessages, botMessage];
      setMessages(finalMessages);
      // Save messages to session storage
      if (typeof window !== 'undefined') {
        sessionStorage.setItem('chatbot-messages', JSON.stringify(finalMessages));
      }

      // Log the interaction for analytics
      if (typeof window !== 'undefined') {
        import('../../utils/api').then(({ logChatInteraction }) => {
          logChatInteraction(
            question,
            response.answer,
            {
              pageContext,
              hasSelectedText: !!selectedTextContext,
              responseTime: Date.now() - startTime
            }
          );
        });
      }

      // Update selected text after submission
      setSelectedText('');
    } catch (error) {
      console.error('Error processing query:', error);

      let errorMessageContent = 'Sorry, I encountered an error processing your request. Please try again.';

      // Provide more specific error messages based on error type
      if (error.name === 'TypeError' && error.message.includes('fetch')) {
        errorMessageContent = 'Unable to connect to the backend service. Please check your connection.';
      } else if (error.message.includes('timeout')) {
        errorMessageContent = 'The request timed out. Please try again.';
      } else if (error.message.includes('400') || error.message.includes('422')) {
        errorMessageContent = 'The request was invalid. Please check your input.';
      } else if (error.message.includes('500')) {
        errorMessageContent = 'The backend service encountered an error. Please try again later.';
      } else if (error.message.includes('503')) {
        errorMessageContent = 'The backend service is temporarily unavailable. Please try again later.';
      }

      const errorMessage = {
        id: `msg-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
        type: 'response',
        content: errorMessageContent,
        timestamp: new Date().toISOString(),
      };

      const updatedMessages = [...prev, errorMessage];
      setMessages(updatedMessages);
      // Save messages to session storage
      if (typeof window !== 'undefined') {
        sessionStorage.setItem('chatbot-messages', JSON.stringify(updatedMessages));
      }
    } finally {
      setIsLoading(false);
    }
  }, [pageContext]);

  return (
    <div className="chatbot-container" role="main" aria-label="Book Assistant Chat Interface">
      <div className="chatbot-header" role="banner">
        <h3>Book Assistant</h3>
        <div
          className={`connection-status ${backendConnected ? 'connected' : 'disconnected'}`}
          aria-label={`Backend connection status: ${backendConnected ? 'connected' : 'disconnected'}`}
          role="status"
        >
          {backendConnected ? '● Connected' : '● Disconnected'}
        </div>
      </div>

      <div
        className="chat-messages"
        aria-live="polite"
        aria-relevant="additions"
        role="log"
      >
        {messages.length === 0 ? (
          <div className="welcome-message" role="alert">
            <p>Ask me questions about the documentation!</p>
            <p>I can use selected text as context to provide more relevant answers.</p>
          </div>
        ) : (
          messages.map((message) => (
            <Message
              key={message.id}
              message={message}
              sources={message.type === 'response' ? [] : []} // In real implementation, sources would come with response
            />
          ))
        )}
        {isLoading && (
          <div className="loading-message" role="status" aria-label="Processing your request">
            <div className="loading-indicator" aria-hidden="true">●●●</div>
            <span>Thinking...</span>
          </div>
        )}
      </div>

      <div className="chat-input-container" role="form" aria-label="Chat input area">
        <ChatInput
          onSubmit={handleSubmit}
          isLoading={isLoading}
          selectedText={selectedText}
        />
      </div>
    </div>
  );
};

export default Chatbot;