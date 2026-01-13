import React from 'react';
import Chatbot from './Chatbot/Chatbot';

/**
 * Docusaurus-specific wrapper for the Chatbot component
 * This component can be imported and used in Docusaurus MDX files
 */
const ChatbotDocusaurus = ({ pageContext, position = 'default' }) => {
  // Get the current page URL as context
  const currentUrl = typeof window !== 'undefined' ? window.location.href : pageContext;

  // Determine container class based on position
  const containerClass = `chatbot-docusaurus-container chatbot-position-${position}`;

  return (
    <div className={containerClass}>
      <Chatbot pageContext={currentUrl} />
    </div>
  );
};

export default ChatbotDocusaurus;