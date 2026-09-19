# NCERT RAG API Documentation

## Overview

FastAPI backend that exposes the existing NCERT RAG engine through clean REST endpoints.

**Base URL:** `http://127.0.0.1:8000`

## Starting the Server

```bash
python start_api.py
```

The server will start on `http://127.0.0.1:8000` with auto-reload enabled.

## Endpoints

### GET /api/health

Health check endpoint to verify the API is running and resources are loaded.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2026-09-19T12:47:55.008499",
  "resources_loaded": true,
  "chunks_count": 785,
  "faiss_index_size": 785
}
```

**Fields:**
- `status`: Always `"healthy"` when the endpoint responds
- `timestamp`: UTC timestamp from `datetime.utcnow().isoformat()`
- `resources_loaded`: `true` only if the Gemini client, FAISS index, and chunk metadata are all loaded
- `chunks_count`: Number of loaded chunk metadata records (`0` if not loaded)
- `faiss_index_size`: `index.ntotal` from the FAISS index (`0` if not loaded)

This endpoint always returns HTTP 200; a partially loaded server reports `false` / `0` rather than an error.

### POST /api/chat

Process a question through the RAG engine. Supports both streaming and non-streaming responses.

**Request Body:**
```json
{
  "message": "Why do we need to balance a chemical equation?",
  "chat_history": [
    {
      "role": "user",
      "content": "previous question"
    },
    {
      "role": "assistant",
      "content": "previous answer"
    }
  ],
  "subject_filter": "All Subjects",
  "stream": false
}
```

**Fields:**
- `message` (required): User's question
- `chat_history` (optional): Array of previous conversation messages, defaults to `[]`
- `subject_filter` (optional): Filter by subject - `"All Subjects"`, `"Science"`, or `"Mathematics"`, defaults to `"All Subjects"`
- `stream` (optional): When `true`, the response is returned as Server-Sent Events instead of JSON. Defaults to `false`

#### Non-Streaming Response

**Response (stream: false):**
```json
{
  "answer": "We need to balance a chemical equation because:\n\n* **Law of Conservation of Mass:** Mass can neither be created nor destroyed...",
  "sources": [
    "Science > Chemical Reactions and Equations > Writing a Chemical Equation",
    "Science > Chemical Reactions and Equations > Balanced Chemical Equations"
  ],
  "retrieval_details": [
    {
      "rank": 1,
      "subject": "Science",
      "chapter": "Chemical Reactions and Equations",
      "section": "Writing a Chemical Equation",
      "distance": 0.6588
    }
  ],
  "updated_history": [
    {
      "role": "user",
      "content": "Why do we need to balance a chemical equation?"
    },
    {
      "role": "assistant",
      "content": "We need to balance a chemical equation because..."
    }
  ]
}
```

#### Streaming Response

**Response (stream: true):**

Server-Sent Events (SSE) format with `Content-Type: text/event-stream`.

**Important:** this is an SSE-compatible response wrapper around the completed RAG response, **not** token-by-token generation. The handler calls `ask_question()`, waits for the complete answer, and then emits that finished answer in a single `content` event. There is no incremental or real-time generation, and the RAG engine is not refactored for streaming generation.

Response headers sent with the stream:
```
Cache-Control: no-cache
Connection: keep-alive
X-Accel-Buffering: no
```

Event types (each frame is `data: <json>\n\n`):

1. **metadata** - Sent first with sources and retrieval details
```
data: {"type": "metadata", "sources": [...], "retrieval_details": [...]}
```

2. **content** - Sent once, containing the complete answer
```
data: {"type": "content", "content": "<the full answer text>"}
```

3. **done** - Final event with updated conversation history
```
data: {"type": "done", "updated_history": [...]}
```

Notes:
- `retrieval_details` in the `metadata` event is the raw list of dicts from the RAG engine, with the same `rank`, `subject`, `chapter`, `section`, and `distance` keys shown in the non-streaming response.
- Because the answer is generated before the stream begins, failures are returned as ordinary JSON HTTP errors (see Error Handling) — there is no `error` event type in the stream.

## Features

### RAG Engine Integration
- Uses existing `ask_question()` function from `scripts/rag_engine.py`
- Preserves FAISS retrieval, subject filtering, query rewriting
- Query rewriting only runs when `chat_history` is non-empty
- Maintains conversation history and source attribution
- Returns retrieval details with distances
- Returns `503` if the Gemini client, FAISS index, or chunk metadata failed to load

### Streaming
- SSE-compatible response wrapper (`text/event-stream`)
- Calls `ask_question()` first, then emits the completed answer in a single `content` event
- Not native Gemini token streaming; `generate_content_stream()` is not used
- Metadata (sources, retrieval details) is emitted before the content event

### Error Handling
- Out-of-scope questions return an appropriate message with empty `sources`
- API errors returned with proper HTTP status codes (`503` when resources are not loaded, `500` on processing errors)
- Streaming errors are returned as JSON error responses, not as SSE events
- Gemini API key kept strictly server-side

### CORS
- Configured for Next.js frontend on ports 3000 and 3001
- Allows credentials and all methods/headers

## Testing

Run the test suite:

```bash
python test_api.py
```

Tests include:
- Health check
- Non-streaming chat
- Streaming chat
- Subject filtering
- Conversation history
- Out-of-scope questions

The streaming test reads the SSE frames and verifies the `metadata`, `content`, and `done` events. Since the API wraps a completed answer, it expects a single `content` event holding the full answer rather than a series of incremental chunks.

## Example Usage

### Python
```python
import requests

response = requests.post(
    "http://127.0.0.1:8000/api/chat",
    json={
        "message": "What is photosynthesis?",
        "subject_filter": "Science",
        "stream": False
    }
)

data = response.json()
print(data['answer'])
```

### JavaScript/TypeScript
```javascript
// Non-streaming
const response = await fetch('http://127.0.0.1:8000/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'What is photosynthesis?',
    subject_filter: 'Science',
    stream: false
  })
});

const data = await response.json();
console.log(data.answer);

// Streaming (SSE wrapper around the completed answer)
const response = await fetch('http://127.0.0.1:8000/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    message: 'What is photosynthesis?',
    subject_filter: 'Science',
    stream: true
  })
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
  const { done, value } = await reader.read();
  if (done) break;

  const chunk = decoder.decode(value);
  const lines = chunk.split('\n');

  for (const line of lines) {
    if (line.startsWith('data: ')) {
      const data = JSON.parse(line.slice(6));

      if (data.type === 'content') {
        console.log(data.content);
      }
    }
  }
}
```

## Dependencies

Required packages (already in requirements.txt):
- `fastapi` - Web framework
- `uvicorn` - ASGI server
- `google-genai` - Gemini API
- `sentence-transformers` - Embeddings
- `faiss-cpu` - Vector search
- `numpy` - Numerical operations
- `python-dotenv` - Environment variables

## Security

- `GEMINI_API_KEY` loaded from `.env` file
- API key never exposed in responses or logs
- Server-side only, no client-side key exposure
- CORS restricted to localhost origins

## Notes

- Server loads all resources on startup (FAISS index, embeddings model, chunks)
- Startup takes ~5-10 seconds to load the embedding model
- Resources are kept in memory for fast inference
- Same RAG logic as Streamlit app - single source of truth
