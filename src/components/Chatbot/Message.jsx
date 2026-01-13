import React from 'react';
import PropTypes from 'prop-types';

/**
 * Message component to display individual chat messages
 * Can render both user questions and AI responses with source references
 */
const Message = ({ message, sources = [] }) => {
  const isUser = message.type === 'question';

  // Use sources from message if available, otherwise use the sources prop
  const messageSources = message.sources || sources;

  return (
    <div className={`message ${isUser ? 'user-message' : 'ai-message'}`}>
      <div className={`message-content ${isUser ? 'user-content' : 'ai-content'}`}>
        <div className="message-text">
          {message.content}
        </div>

        {/* Display sources if this is a response and sources exist */}
        {!isUser && messageSources && messageSources.length > 0 && (
          <div className="sources-section">
            <h4 className="sources-title">Sources:</h4>
            <ul className="sources-list">
              {messageSources.map((source, index) => (
                <li key={source.id || `source-${index}`} className="source-item">
                  <a
                    href={source.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="source-link"
                  >
                    {source.title}
                  </a>
                  {source.confidence !== undefined && (
                    <span className="confidence">({(source.confidence * 100).toFixed(1)}%)</span>
                  )}
                  {source.excerpt && (
                    <div className="source-excerpt">
                      "{source.excerpt.substring(0, 100)}{source.excerpt.length > 100 ? '...' : ''}"
                    </div>
                  )}
                </li>
              ))}
            </ul>
          </div>
        )}
      </div>
      <div className="message-timestamp">
        {new Date(message.timestamp).toLocaleTimeString()}
      </div>
    </div>
  );
};

Message.propTypes = {
  message: PropTypes.shape({
    id: PropTypes.string,
    type: PropTypes.oneOf(['question', 'response']).isRequired,
    content: PropTypes.string.isRequired,
    timestamp: PropTypes.oneOfType([PropTypes.string, PropTypes.instanceOf(Date)]).isRequired,
  }).isRequired,
  sources: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      title: PropTypes.string.isRequired,
      url: PropTypes.string.isRequired,
      excerpt: PropTypes.string,
      confidence: PropTypes.number.isRequired,
    })
  ),
};

export default Message;