import React, { useState, useRef } from 'react';
import PropTypes from 'prop-types';

/**
 * ChatInput component for user to enter questions
 * Handles text input and submission
 */
const ChatInput = ({ onSubmit, isLoading = false, selectedText = '' }) => {
  const [inputValue, setInputValue] = useState('');
  const textareaRef = useRef(null);

  const handleSubmit = (e) => {
    e.preventDefault();

    // Limit selected text to 5000 characters as per data model
    const processedSelectedText = selectedText.length > 5000
      ? selectedText.substring(0, 5000)
      : selectedText;

    if (inputValue.trim() || processedSelectedText.trim()) {
      onSubmit(inputValue, processedSelectedText);
      setInputValue('');
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      if (inputValue.trim() || selectedText.trim()) {
        handleSubmit(e);
      }
    }
  };

  return (
    <form className="chat-input-form" onSubmit={handleSubmit}>
      {selectedText && (
        <div className="selected-text-preview">
          <span className="selected-text-label">Selected text:</span>
          <div className="selected-text-content">
            "{selectedText.substring(0, 100)}{selectedText.length > 100 ? '...' : ''}"
          </div>
        </div>
      )}
      <div className="input-container">
        <textarea
          ref={textareaRef}
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Ask a question about the documentation..."
          className="chat-textarea"
          rows="3"
          disabled={isLoading}
        />
        <button
          type="submit"
          className={`submit-button ${isLoading ? 'loading' : ''}`}
          disabled={isLoading || (!inputValue.trim() && !selectedText.trim())}
        >
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </div>
    </form>
  );
};

ChatInput.propTypes = {
  onSubmit: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,
  selectedText: PropTypes.string,
};

export default ChatInput;