/**
 * Structured answer presentation for learning responses
 * Provides editorial-style formatting for key ideas, examples, equations, and sources
 */

import React from 'react';
import { MarkdownRenderer } from './MarkdownRenderer';

interface StructuredAnswerProps {
  content: string;
  sources?: string[];
  retrievalDetails?: Array<{
    rank: number;
    subject: string;
    chapter: string;
    section: string;
    distance: number;
  }>;
}

/**
 * Key Idea callout component
 * Subtle elevated surface with emerald accent
 */
function KeyIdea({ children }: { children: React.ReactNode }) {
  return (
    <div className="my-6 px-5 py-4 bg-[var(--color-surface-elevated)] border-l-2 border-[var(--color-accent)] rounded-md">
      <div className="text-label text-[var(--color-accent)] mb-2">KEY IDEA</div>
      <div className="text-answer-body">{children}</div>
    </div>
  );
}

/**
 * Example section component
 * Indented with subtle border
 */
function ExampleSection({ children, title }: { children: React.ReactNode; title?: string }) {
  return (
    <div className="my-6 pl-5 border-l-2 border-[var(--color-border)]">
      <div className="text-label text-[var(--color-text-secondary)] mb-3">
        {title || 'EXAMPLE'}
      </div>
      <div className="text-answer-body space-y-3">{children}</div>
    </div>
  );
}

/**
 * Chemical equation or mathematical formula display
 * Centered with subtle background
 */
function EquationDisplay({ children }: { children: React.ReactNode }) {
  // Convert subscript numbers to proper subscript characters
  const formatEquation = (text: string) => {
    // Replace common subscripts: H2 -> H₂, O2 -> O₂, etc.
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
    <div className="my-5 px-8 py-4 bg-[rgba(255,255,255,0.02)] border border-[rgba(255,255,255,0.04)] rounded-lg text-center">
      <div className="text-lg text-[var(--color-text-primary)] tracking-wide" style={{ fontFamily: 'var(--font-serif)' }}>
        {formattedContent}
      </div>
    </div>
  );
}

/**
 * NCERT Source - Compact editorial treatment
 * Shows only the top/highest-ranked source
 */
function NCERTSource({
  sources,
  retrievalDetails
}: {
  sources: string[];
  retrievalDetails?: Array<{
    rank: number;
    subject: string;
    chapter: string;
    section: string;
    distance: number;
  }>;
}) {
  // Show only the top source
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

/**
 * Parse answer content and identify structural elements
 */
function parseAnswer(content: string) {
  const sections: Array<{ type: string; content: string; title?: string }> = [];
  const lines = content.split('\n');

  let currentSection: { type: string; content: string; title?: string } | null = null;
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];
    const trimmed = line.trim();

    // Skip empty lines between sections
    if (!trimmed) {
      if (currentSection && currentSection.content.trim()) {
        sections.push(currentSection);
        currentSection = null;
      }
      i++;
      continue;
    }

    // Detect KEY IDEA: heading
    if (trimmed.match(/^KEY IDEA:/i)) {
      if (currentSection) sections.push(currentSection);
      currentSection = { type: 'key-idea', content: '' };
      // Skip the heading line, content starts next line
      i++;
      continue;
    }

    // Detect EXAMPLE: or Example heading
    if (trimmed.match(/^EXAMPLE:/i) || trimmed.match(/^Example\s*\d*/i)) {
      if (currentSection) sections.push(currentSection);
      const title = trimmed.replace(/^EXAMPLE:\s*/i, '').replace(/^Example\s*/i, 'Example ').trim();
      currentSection = { type: 'example', content: '', title: title || undefined };
      i++;
      continue;
    }

    // Detect EXPLANATION: heading
    if (trimmed.match(/^EXPLANATION:/i)) {
      if (currentSection) sections.push(currentSection);
      currentSection = { type: 'text', content: '' };
      i++;
      continue;
    }

    // Detect standalone chemical equations (arrows and chemical formulas)
    if (trimmed.match(/^[A-Z][a-z]?[₀-₉0-9]*(\s*\+\s*[A-Z][a-z]?[₀-₉0-9]*)+\s*(→|⟶|⇌)\s*[A-Z][a-z]?/)) {
      if (currentSection && currentSection.type === 'example') {
        // Keep equation within example
        currentSection.content += '\n[EQUATION]' + trimmed + '[/EQUATION]\n';
      } else {
        if (currentSection) sections.push(currentSection);
        sections.push({ type: 'equation', content: trimmed });
        currentSection = null;
      }
      i++;
      continue;
    }

    // Regular content
    if (!currentSection) {
      currentSection = { type: 'text', content: '' };
    }

    currentSection.content += (currentSection.content ? '\n' : '') + line;
    i++;
  }

  if (currentSection && currentSection.content.trim()) {
    sections.push(currentSection);
  }

  return sections;
}

export function StructuredAnswer({ content, sources, retrievalDetails }: StructuredAnswerProps) {
  const sections = parseAnswer(content);

  return (
    <div className="space-y-1">
      {sections.map((section, idx) => {
        if (section.type === 'key-idea') {
          return (
            <KeyIdea key={idx}>
              <MarkdownRenderer content={section.content} />
            </KeyIdea>
          );
        }

        if (section.type === 'example') {
          // Check for embedded equations
          const equationMatch = section.content.match(/\[EQUATION\](.*?)\[\/EQUATION\]/);
          if (equationMatch) {
            const beforeEq = section.content.substring(0, section.content.indexOf('[EQUATION]')).trim();
            const afterEq = section.content.substring(section.content.indexOf('[/EQUATION]') + 11).trim();

            return (
              <ExampleSection key={idx} title={section.title}>
                {beforeEq && <MarkdownRenderer content={beforeEq} />}
                <EquationDisplay>{equationMatch[1].trim()}</EquationDisplay>
                {afterEq && <MarkdownRenderer content={afterEq} />}
              </ExampleSection>
            );
          }

          return (
            <ExampleSection key={idx} title={section.title}>
              <MarkdownRenderer content={section.content} />
            </ExampleSection>
          );
        }

        if (section.type === 'equation') {
          return <EquationDisplay key={idx}>{section.content}</EquationDisplay>;
        }

        // Regular text
        return (
          <div key={idx} className="text-answer-body">
            <MarkdownRenderer content={section.content} />
          </div>
        );
      })}

      {sources && sources.length > 0 && (
        <NCERTSource sources={sources} retrievalDetails={retrievalDetails} />
      )}
    </div>
  );
}
