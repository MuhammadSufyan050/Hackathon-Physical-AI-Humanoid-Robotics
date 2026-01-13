// API utility functions for Docusaurus RAG Chatbot
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8001';

/**
 * Query the backend retrieval agent
 * @param {string} question - The question to ask
 * @param {string} selectedText - Optional selected text for context
 * @param {string} pageContext - Optional page context
 * @returns {Promise<Object>} Response from the backend
 */
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

    const data = await response.json();

    // Check if response indicates no relevant content found
    if (data.status === 'no_results' || (data.answer && data.answer.toLowerCase().includes('no relevant content'))) {
      console.warn('No relevant content found for the query');
    }

    return data;
  } catch (error) {
    console.error('API call failed:', error);
    throw error;
  }
};

/**
 * Check backend health status
 * @returns {Promise<Object>} Health status response
 */
export const checkHealth = async () => {
  try {
    const response = await fetch(`${API_BASE_URL}/health`);

    if (!response.ok) {
      throw new Error(`Health check failed with status: ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Health check failed:', error);
    throw error;
  }
};

/**
 * Query with timeout handling
 * @param {string} question - The question to ask
 * @param {string} selectedText - Optional selected text for context
 * @param {string} pageContext - Optional page context
 * @param {number} timeoutMs - Timeout in milliseconds (default 30000ms)
 * @returns {Promise<Object>} Response from the backend
 */
export const queryBackendWithTimeout = async (question, selectedText = '', pageContext = '', timeoutMs = 30000) => {
  // Create a timeout promise
  const timeoutPromise = new Promise((_, reject) => {
    setTimeout(() => reject(new Error('Request timeout')), timeoutMs);
  });

  // Race the API call against the timeout
  const apiPromise = queryBackend(question, selectedText, pageContext);

  return Promise.race([apiPromise, timeoutPromise]);
};

/**
 * Verify backend API endpoints are accessible
 * @returns {Promise<boolean>} True if endpoints are accessible, false otherwise
 */
export const verifyBackendConnection = async () => {
  try {
    await checkHealth();
    return true;
  } catch (error) {
    console.error('Backend connection verification failed:', error);
    return false;
  }
};

/**
 * Log chat interaction for analytics
 * @param {string} question - The user's question
 * @param {string} response - The AI's response
 * @param {Object} metadata - Additional metadata about the interaction
 */
export const logChatInteraction = (question, response, metadata = {}) => {
  const interaction = {
    timestamp: new Date().toISOString(),
    question,
    response,
    metadata,
    userAgent: typeof window !== 'undefined' ? navigator.userAgent : 'server',
    pageUrl: typeof window !== 'undefined' ? window.location.href : 'unknown'
  };

  // In a real implementation, this would send to an analytics service
  console.log('Chat interaction logged:', interaction);

  // For now, just store in localStorage for debugging
  if (typeof window !== 'undefined') {
    const logs = JSON.parse(localStorage.getItem('chatLogs') || '[]');
    logs.push(interaction);
    // Keep only the last 100 logs to prevent storage bloat
    if (logs.length > 100) {
      logs.shift();
    }
    localStorage.setItem('chatLogs', JSON.stringify(logs));
  }
};