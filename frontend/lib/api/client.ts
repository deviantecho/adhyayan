import { API_CONFIG } from './types';
import type {
  ChatRequest,
  ChatResponse,
  HealthResponse,
  SSEMessage,
} from './types';

/**
 * API Client for NCERT RAG backend
 */
class APIClient {
  private baseURL: string;

  constructor(baseURL?: string) {
    this.baseURL = baseURL || API_CONFIG.baseURL;
  }

  /**
   * Health check endpoint
   */
  async checkHealth(): Promise<HealthResponse> {
    const response = await fetch(`${this.baseURL}${API_CONFIG.endpoints.health}`);

    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }

    return response.json();
  }

  /**
   * Chat endpoint - non-streaming
   */
  async chat(request: ChatRequest): Promise<ChatResponse> {
    const response = await fetch(`${this.baseURL}${API_CONFIG.endpoints.chat}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        ...request,
        stream: false,
      }),
    });

    if (!response.ok) {
      // Parse error response
      let errorMessage = 'Unknown error';
      try {
        const errorData = await response.json();
        errorMessage = errorData.detail || errorData.message || JSON.stringify(errorData);
      } catch {
        errorMessage = await response.text();
      }

      // Check for specific error patterns
      if (response.status === 429 || errorMessage.includes('RESOURCE_EXHAUSTED') || errorMessage.includes('quota')) {
        throw new Error('QUOTA_EXCEEDED: Service quota exceeded');
      } else if (response.status === 503) {
        throw new Error('SERVICE_UNAVAILABLE: Service temporarily unavailable');
      }

      throw new Error(`Chat request failed: ${errorMessage}`);
    }

    return response.json();
  }

  /**
   * Chat endpoint - streaming
   *
   * Note: Current backend implementation returns complete answer in SSE format,
   * not true token-by-token streaming. This is a wrapper around the complete response.
   */
  async chatStream(
    request: ChatRequest,
    onMessage: (event: SSEMessage) => void,
    onError?: (error: Error) => void,
    onComplete?: () => void
  ): Promise<void> {
    try {
      const response = await fetch(`${this.baseURL}${API_CONFIG.endpoints.chat}`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...request,
          stream: true,
        }),
      });

      if (!response.ok) {
        throw new Error(`Chat stream failed: ${response.statusText}`);
      }

      if (!response.body) {
        throw new Error('Response body is null');
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();

        if (done) {
          onComplete?.();
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6)) as SSEMessage;
              onMessage(data);

              if (data.type === 'error') {
                onError?.(new Error(data.error));
              }
            } catch (e) {
              console.error('Failed to parse SSE message:', e);
            }
          }
        }
      }
    } catch (error) {
      onError?.(error instanceof Error ? error : new Error(String(error)));
    }
  }
}

// Singleton instance
export const apiClient = new APIClient();

// Named exports for convenience
export const checkHealth = () => apiClient.checkHealth();
export const chat = (request: ChatRequest) => apiClient.chat(request);
export const chatStream = (
  request: ChatRequest,
  onMessage: (event: SSEMessage) => void,
  onError?: (error: Error) => void,
  onComplete?: () => void
) => apiClient.chatStream(request, onMessage, onError, onComplete);
