# API Contract: Docusaurus RAG Chatbot Integration

## Overview

This document defines the API contracts for the communication between the Docusaurus frontend chatbot and the retrieval agent backend.

## Base URL

`http://localhost:8000` (local development)

## Endpoints

### POST /query

Submit a question to the retrieval agent and receive a grounded response.

#### Request

**Headers:**
- `Content-Type: application/json`
- `Accept: application/json`

**Body:**
```json
{
  "question": "string (required)",
  "selectedText": "string (optional)",
  "pageContext": "string (optional)"
}
```

**Parameters:**
- `question`: The natural language question from the user
- `selectedText`: Text selected by the user on the current page (for additional context)
- `pageContext`: URL or identifier of the current page (for context)

#### Response

**Success Response (200 OK):**
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
      "confidence": "number (0-1)"
    }
  ],
  "status": "success"
}
```

**Error Response (400 Bad Request):**
```json
{
  "error": "string",
  "message": "string"
}
```

**Server Error Response (500 Internal Server Error):**
```json
{
  "error": "string",
  "message": "string"
}
```

### GET /health

Check the health status of the retrieval agent backend.

#### Response

**Success Response (200 OK):**
```json
{
  "status": "healthy",
  "timestamp": "string (ISO 8601 date string)"
}
```

### POST /chat

Alternative chat endpoint with conversation history support.

#### Request

**Headers:**
- `Content-Type: application/json`
- `Accept: application/json`

**Body:**
```json
{
  "question": "string (required)",
  "selectedText": "string (optional)",
  "pageContext": "string (optional)",
  "sessionId": "string (optional)",
  "history": [
    {
      "type": "question|response",
      "content": "string"
    }
  ]
}
```

#### Response

**Success Response (200 OK):**
```json
{
  "id": "string",
  "questionId": "string",
  "sessionId": "string",
  "answer": "string",
  "sources": [
    {
      "title": "string",
      "url": "string",
      "excerpt": "string",
      "confidence": "number (0-1)"
    }
  ],
  "status": "success"
}
```

## Error Codes

- `200`: Success
- `400`: Bad Request - Invalid input parameters
- `404`: Not Found - Endpoint does not exist
- `422`: Unprocessable Entity - Input validation failed
- `500`: Internal Server Error - Backend processing error
- `503`: Service Unavailable - Backend service is temporarily unavailable

## Data Types

### Question
- `question`: string (1-1000 characters)
- `selectedText`: string (0-5000 characters, optional)
- `pageContext`: string (optional)

### Response
- `id`: string (unique identifier)
- `questionId`: string (reference to the original question)
- `answer`: string (the response text)
- `sources`: array of SourceReference objects
- `status`: string (success|error|timeout)

### SourceReference
- `title`: string (title of the source document)
- `url`: string (URL to the source)
- `excerpt`: string (relevant text snippet)
- `confidence`: number (0-1, indicating relevance)

## Authentication

No authentication required for local development. For production deployments, API key authentication may be implemented via the `Authorization` header.

## Rate Limiting

The backend may implement rate limiting to prevent abuse. Clients should handle HTTP 429 responses gracefully.

## Timeouts

API calls should implement reasonable timeouts (suggested: 30 seconds) to handle slow backend responses.