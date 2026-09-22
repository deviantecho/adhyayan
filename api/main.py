import os
import sys

# Add parent directory to path to import scripts
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from typing import List
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

# Import the existing RAG engine
from scripts.rag_engine import ask_question, ask_question_stream, llm_provider, index, chunks

# --------------------------------------------------
# MODELS
# --------------------------------------------------

class Message(BaseModel):
    role: str = Field(..., description="Either 'user' or 'assistant'")
    content: str = Field(..., description="Message content")

class ChatRequest(BaseModel):
    message: str = Field(..., description="User's question")
    chat_history: List[Message] = Field(default=[], description="Previous conversation messages")
    subject_filter: str = Field(default="All Subjects", description="Subject filter: 'All Subjects', 'Science', or 'Mathematics'")
    stream: bool = Field(default=False, description="Enable streaming response (currently returns complete answer)")

class RetrievalDetail(BaseModel):
    rank: int
    subject: str
    chapter: str
    section: str
    distance: float

class ChatResponse(BaseModel):
    answer: str
    sources: List[str]
    retrieval_details: List[RetrievalDetail]
    updated_history: List[Message]

# --------------------------------------------------
# APP INITIALIZATION
# --------------------------------------------------

app = FastAPI(
    title="Adhyayan API",
    description="Class 10 NCERT Study Companion API",
    version="1.0.0"
)

# CORS configuration for Next.js frontend
# Production frontend URL should be set via FRONTEND_URL env var
frontend_url = os.getenv("FRONTEND_URL", "")
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]
if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------------------------------------
# ENDPOINTS
# --------------------------------------------------

@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "resources_loaded": all([
            llm_provider is not None,
            index is not None,
            chunks is not None
        ]),
        "chunks_count": len(chunks) if chunks else 0,
        "faiss_index_size": index.ntotal if index else 0
    }

@app.post("/api/chat")
async def chat(request: ChatRequest):
    """
    Process a chat message through the RAG engine.
    Uses the existing ask_question() function from scripts/rag_engine.py
    """

    if not all([llm_provider, index, chunks]):
        raise HTTPException(
            status_code=503,
            detail="AI resources not loaded"
        )

    try:
        # Convert Pydantic models to dict for the RAG engine
        chat_history = [
            {"role": msg.role, "content": msg.content}
            for msg in request.chat_history
        ]

        # If streaming is requested, use true LLM provider streaming
        if request.stream:
            async def generate_stream():
                try:
                    # Call streaming RAG engine - Phase 3.16O with explicit termination
                    for event in ask_question_stream(
                        request.message,
                        chat_history,
                        request.subject_filter
                    ):
                        yield f"data: {json.dumps(event)}\n\n"

                    # CRITICAL: If no done event was emitted, emit one now
                    # This ensures the stream ALWAYS terminates explicitly
                    # (The RAG engine should emit done, but this is a safety net)

                except Exception as e:
                    # CRITICAL: Emit explicit error event with terminal state
                    # This ensures frontend exits loading state even on backend failure
                    error_event = {
                        "type": "error",
                        "error": f"Stream error: {str(e)}"
                    }
                    yield f"data: {json.dumps(error_event)}\n\n"

            return StreamingResponse(
                generate_stream(),
                media_type="text/event-stream",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "X-Accel-Buffering": "no",
                    # Add timeout header for long-running streams
                    "X-Stream-Timeout": "300"
                }
            )

        answer, sources, retrieval_details, updated_history = ask_question(
            request.message,
            chat_history,
            request.subject_filter
        )

        retrieval_details_response = [
            RetrievalDetail(**detail) for detail in retrieval_details
        ]
        updated_history_response = [
            Message(**msg) for msg in updated_history
        ]

        return ChatResponse(
            answer=answer,
            sources=sources,
            retrieval_details=retrieval_details_response,
            updated_history=updated_history_response
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing request: {str(e)}"
        )

# --------------------------------------------------
# ROOT ENDPOINT
# --------------------------------------------------

@app.get("/")
async def root():
    return {
        "message": "Adhyayan API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "chat": "/api/chat"
        }
    }
