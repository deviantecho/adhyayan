/**
 * Normalized Answer Contract - Phase 3.16O
 * Provider-agnostic semantic answer structure
 *
 * This is the SINGLE contract between backend and frontend.
 * Frontend renders THIS structure, never raw LLM text.
 */

// ============================================================================
// BLOCK TYPES
// ============================================================================

/**
 * Markdown content block - rendered through MarkdownRenderer
 */
export interface MarkdownBlock {
  type: 'markdown';
  content: string;
}

/**
 * Semantic equation (chemistry, mathematics, physics)
 * Rendered through EquationDisplay component
 */
export interface EquationBlock {
  type: 'equation';
  content: string;
}

/**
 * Example section with nested blocks
 */
export interface ExampleBlock {
  type: 'example';
  title: string;
  blocks: Array<MarkdownBlock | EquationBlock>;
}

/**
 * Union type for all content blocks
 */
export type ContentBlock = MarkdownBlock | EquationBlock | ExampleBlock;

// ============================================================================
// ANSWER TYPE
// ============================================================================

/**
 * Normalized provider-independent answer structure.
 *
 * Structure:
 * - keyIdea: The central concept (optional but expected for educational answers)
 * - explanation: Main explanation content (optional but expected)
 * - blocks: Semantic content blocks in document order
 * - sources: NCERT source references
 * - retrievalDetails: Detailed retrieval information
 */
export interface Answer {
  keyIdea: string | null;
  explanation: string | null;
  blocks: ContentBlock[];
  sources: string[];
  retrievalDetails: Array<{
    rank: number;
    subject: string;
    chapter: string;
    section: string;
    distance: number;
  }>;
}

// ============================================================================
// SSE MESSAGE TYPES
// ============================================================================

/**
 * SSE message from backend
 *
 * Stream lifecycle:
 * 1. metadata → sources and retrieval details
 * 2. content × N → streaming text chunks
 * 3. done → normalized Answer object
 *
 * OR (error path):
 * 1. metadata (if available)
 * 2. error → error message
 */
export type SSEMessage =
  | { type: 'metadata'; sources: string[]; retrieval_details: Answer['retrievalDetails'] }
  | { type: 'content'; content: string }
  | { type: 'done'; updated_history: Message[]; answer: Answer }
  | { type: 'error'; error: string };

/**
 * Chat message structure
 */
export interface Message {
  role: 'user' | 'assistant';
  content: string;
  sources?: string[];
  retrievalDetails?: Answer['retrievalDetails'];
  isStreaming?: boolean;
  answer?: Answer; // Normalized answer from done event
}

// ============================================================================
// TYPE GUARDS
// ============================================================================

export function isMarkdownBlock(block: ContentBlock): block is MarkdownBlock {
  return block.type === 'markdown';
}

export function isEquationBlock(block: ContentBlock): block is EquationBlock {
  return block.type === 'equation';
}

export function isExampleBlock(block: ContentBlock): block is ExampleBlock {
  return block.type === 'example';
}
