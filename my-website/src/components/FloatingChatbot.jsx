import React, { useState } from 'react';
import ChatbotDocusaurus from './ChatbotDocusaurus';
import './FloatingChatbot.css';

const FloatingChatbot = () => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleChat = () => {
    setIsOpen(!isOpen);
  };

  return (
    <div className="floating-chatbot">
      {isOpen && (
        <div className="chatbot-window">
          <div className="chatbot-header">
            <h3>Book Assistant</h3>
            <button className="close-button" onClick={toggleChat}>
              ×
            </button>
          </div>
          <div className="chatbot-content">
            <ChatbotDocusaurus />
          </div>
        </div>
      )}
      <button className={`chatbot-toggle ${isOpen ? 'open' : ''}`} onClick={toggleChat}>
        {isOpen ? '×' : '💬'}
      </button>
    </div>
  );
};

export default FloatingChatbot;