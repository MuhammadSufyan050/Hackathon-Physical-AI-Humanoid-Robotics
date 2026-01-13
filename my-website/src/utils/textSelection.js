// Text selection utility functions for Docusaurus RAG Chatbot

/**
 * Get the currently selected text from the page
 * @returns {string} The selected text, or empty string if no selection
 */
export const getSelectedText = () => {
  const selection = window.getSelection();
  return selection.toString().trim();
};

/**
 * Get detailed information about the current text selection
 * @returns {Object|null} Selection info or null if no selection
 */
export const getSelectedTextInfo = () => {
  const selection = window.getSelection();

  if (!selection.toString().trim()) {
    return null;
  }

  const range = selection.rangeCount > 0 ? selection.getRangeAt(0) : null;

  return {
    text: selection.toString().trim(),
    range: range,
    startContainer: range ? range.startContainer : null,
    startOffset: range ? range.startOffset : null,
    endContainer: range ? range.endContainer : null,
    endOffset: range ? range.endOffset : null
  };
};

/**
 * Add a listener for text selection changes
 * @param {Function} callback - Function to call when selection changes
 * @returns {Function} Cleanup function to remove the listener
 */
export const addSelectionListener = (callback) => {
  const handleSelection = () => {
    const selectedText = getSelectedText();
    callback(selectedText);
  };

  // Listen for both mouse and keyboard events
  document.addEventListener('mouseup', handleSelection);
  document.addEventListener('keyup', handleSelection);

  // Return cleanup function
  return () => {
    document.removeEventListener('mouseup', handleSelection);
    document.removeEventListener('keyup', handleSelection);
  };
};

/**
 * Check if text is currently selected on the page
 * @returns {boolean} True if text is selected, false otherwise
 */
export const isTextSelected = () => {
  return window.getSelection().toString().trim().length > 0;
};

/**
 * Clear any current text selection
 */
export const clearSelection = () => {
  if (window.getSelection) {
    window.getSelection().removeAllRanges();
  } else if (document.selection) {
    document.selection.empty();
  }
};