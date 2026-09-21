/**
 * Structured answer presentation for learning responses
 * Phase 3.16O: Consumes ONLY normalized Answer object from backend
 *
 * Architecture:
 * Backend normalizes LLM response → SSE done event with Answer → Frontend renders structured data
 * NO fragile XML parsing during streaming
 * NO inference of semantic structure from prose
 */

import React from 'react';
import { MarkdownRenderer } from './MarkdownRenderer';
import type { Answer, ContentBlock, MarkdownBlock, EquationBlock, ExampleBlock } from '../lib/types/answer';

// ============================================================================
// VISUAL COMPONENTS
// ============================================================================

/**
 * Key Idea callout component
 * Phase 3.16O: MUST use approved green box design
 */
function KeyIdea({ children }: { children: React.ReactNode }) {
  return (
    <div className="my-6 px-5 py-4 bg-[rgba(255,255,255,0.035)] border border-[rgba(255,255,255,0.07)] border-l-[3px] border-l-[var(--color-accent)] rounded-lg">
      <div className="text-[11px] font-semibold tracking-[0.1em] text-[var(--color-accent)] mb-3 uppercase">
        Key Idea
      </div>
      <div className="text-[15px] leading-[1.7] text-[var(--color-text-primary)]">{children}</div>
    </div>
  );
}

/**
 * Example section component
 * Renders nested blocks (text + equations)
 */
function ExampleSection({
  title,
  blocks
}: {
  title: string;
  blocks: Array<MarkdownBlock | EquationBlock>;
}) {
  return (
    <div className="my-6">
      <div className="text-[11px] font-semibold tracking-[0.1em] text-[var(--color-text-secondary)] mb-4 uppercase">
        {title}
      </div>
      <div className="text-[15px] leading-[1.7] text-[var(--color-text-primary)]">
        {blocks.map((block, idx) => {
          if (block.type === 'markdown') {
            return <MarkdownRenderer key={idx} content={block.content} />;
          }
          if (block.type === 'equation') {
            return <EquationDisplay key={idx}>{block.content}</EquationDisplay>;
          }
          return null;
        })}
      </div>
    </div>
  );
}

/**
 * Chemical equation or mathematical formula display
 * Phase 3.16O: MUST use approved grey box design
 */
function EquationDisplay({ children }: { children: React.ReactNode }) {
  // Convert subscript numbers to proper subscript characters
  const formatEquation = (text: string) => {
    return text
      .replace(/(\w)(\d+)/g, (_, letter, num) => {
        const subscripts: Record<string, string> = {
          '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
          '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉'
        };
        return letter + num.split('').map((d: string) => subscripts[d] || d).join('');
      });
  };

  const formattedContent = typeof children === 'string' ? formatEquation(children) : children;

  return (
    <div className="my-5 mx-auto max-w-fit px-6 py-5 bg-[rgba(255,255,255,0.035)] border border-[rgba(255,255,255,0.06)] rounded-lg">
      <div className="text-[18px] text-[var(--color-text-primary)] leading-relaxed font-serif text-center">
        {formattedContent}
      </div>
    </div>
  );
}

/**
 * NCERT Source - Compact editorial treatment
 */
function NCERTSource({
  sources,
  retrievalDetails
}: {
  sources: string[];
  retrievalDetails?: Answer['retrievalDetails'];
}) {
  const topSource = sources && sources.length > 0 ? sources[0] : null;
  const topDetail = retrievalDetails && retrievalDetails.length > 0 ? retrievalDetails[0] : null;

  if (!topSource) return null;

  return (
    <div className="mt-6 flex items-start gap-2.5 text-[13px]">
      <svg
        className="w-3.5 h-3.5 text-[var(--color-text-tertiary)] flex-shrink-0 mt-0.5"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"
        />
      </svg>
      <div className="flex-1">
        <div className="text-label text-[var(--color-text-secondary)] mb-1">NCERT SOURCE</div>
        <div className="text-[var(--color-text-tertiary)] leading-relaxed">
          {topSource}
          {topDetail?.section && ` · ${topDetail.section}`}
        </div>
      </div>
    </div>
  );
}

// ============================================================================
// BLOCK RENDERER
// ============================================================================

/**
 * Render a single content block
 * Phase 3.16O: Each block type has deterministic rendering
 */
function renderBlock(block: ContentBlock, index: number): React.ReactNode {
  switch (block.type) {
    case 'markdown':
      return (
        <div key={index} className="text-answer-body">
          <MarkdownRenderer content={block.content} />
        </div>
      );

    case 'equation':
      return <EquationDisplay key={index}>{block.content}</EquationDisplay>;

    case 'example':
      return (
        <ExampleSection key={index} title={block.title} blocks={block.blocks} />
      );

    default:
      return null;
  }
}

// ============================================================================
// MAIN COMPONENT
// ============================================================================

export function StructuredAnswer({ answer }: { answer: Answer }) {
  // Phase 3.16O: Render ONLY from normalized Answer object
  // No XML parsing, no regex, no inference from prose

  return (
    <div className="space-y-1">
      {/* Key Idea - ALWAYS green box when present */}
      {answer.keyIdea && (
        <KeyIdea>
          <MarkdownRenderer content={answer.keyIdea} />
        </KeyIdea>
      )}

      {/* Explanation - rendered as markdown */}
      {answer.explanation && (
        <div className="text-answer-body">
          <MarkdownRenderer content={answer.explanation} />
        </div>
      )}

      {/* Content blocks in document order */}
      {answer.blocks.map((block, idx) => renderBlock(block, idx))}

      {/* Sources */}
      {answer.sources && answer.sources.length > 0 && (
        <NCERTSource
          sources={answer.sources}
          retrievalDetails={answer.retrievalDetails}
        />
      )}
    </div>
  );
}

// ============================================================================
// LEGACY COMPONENT (Backward Compatibility)
// ============================================================================

/**
 * Legacy wrapper for old raw content format
 * Phase 3.16O: This should rarely be used - only for old chat history
 *
 * @deprecated Use StructuredAnswer with Answer object instead
 */
export function StructuredAnswerLegacy({
  content,
  sources,
  retrievalDetails
}: {
  content: string;
  sources?: string[];
  retrievalDetails?: Answer['retrievalDetails'];
}) {
  // This is a fallback for old chat history that doesn't have normalized answer
  // It creates a simple Answer object from the raw content
  const fallbackAnswer: Answer = {
    keyIdea: null,
    explanation: null,
    blocks: [{ type: 'markdown', content }],
    sources: sources || [],
    retrievalDetails: retrievalDetails || []
  };

  return <StructuredAnswer answer={fallbackAnswer} />;
}