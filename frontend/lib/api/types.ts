// API Configuration
export const API_CONFIG = {
  baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://127.0.0.1:8000',
  endpoints: {
    health: '/api/health',
    chat: '/api/chat',
  },
} as const;

// Import Answer type from normalized answer schema
import type { Answer } from '../types/answer';

// API Types
export interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
  retrievalDetails?: Answer['retrievalDetails'];
  isStreaming?: boolean;
  answer?: Answer; // Phase 3.16O: Normalized Answer object from done event
}

export interface ChatRequest {
  message: string;
  chat_history: Message[];
  subject_filter: 'All Subjects' | 'Science' | 'Mathematics';
  stream?: boolean;
}

export interface RetrievalDetail {
  rank: number;
  subject: string;
  chapter: string;
  section: string;
  distance: number;
}

export interface ChatResponse {
  answer: string;
  sources: string[];
  retrieval_details: RetrievalDetail[];
  updated_history: Message[];
}

export interface HealthResponse {
  status: string;
  timestamp: string;
  resources_loaded: boolean;
  chunks_count: number;
  faiss_index_size: number;
}

// SSE Event Types for streaming
export type SSEMessageType = 'metadata' | 'content' | 'done' | 'error';

export interface SSEMetadata {
  type: 'metadata';
  sources: string[];
  retrieval_details: RetrievalDetail[];
}

export interface SSEContent {
  type: 'content';
  content: string;
}

export interface SSEDone {
  type: 'done';
  updated_history: Message[];
  answer?: Answer; // Phase 3.16O: Normalized Answer object
}

export interface SSEError {
  type: 'error';
  error: string;
}

export type SSEMessage = SSEMetadata | SSEContent | SSEDone | SSEError;
