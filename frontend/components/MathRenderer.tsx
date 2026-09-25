/**
 * Math Renderer Component
 * Renders LaTeX mathematical and chemical equations using KaTeX
 *
 * Features:
 * - Auto-detects LaTeX notation in text
 * - Supports inline and display math
 * - Fallback to ASCII subscript conversion for plain text
 * - Error handling for malformed LaTeX
 * - Dark mode compatible
 */

import React from 'react';
import katex from 'katex';

interface MathRendererProps {
  children: string;
  displayMode?: boolean;
  forceLatex?: boolean;
}

/**
 * Render a single LaTeX expression with KaTeX.
 * A null result tells the component to render escaped, readable source text.
 */
function renderLatex(latex: string, displayMode: boolean = false): string | null {
  try {
    return katex.renderToString(latex, {
      displayMode,
      throwOnError: true,
      output: 'html',
      trust: false,
      strict: false,
    });
  } catch {
    return null;
  }
}

/**
 * Convert plain ASCII subscripts to Unicode (backward compatibility)
 */
function convertAsciiSubscripts(text: string): string {
  const subscripts: Record<string, string> = {
    '0': '₀', '1': '₁', '2': '₂', '3': '₃', '4': '₄',
    '5': '₅', '6': '₆', '7': '₇', '8': '₈', '9': '₉'
  };

  return text.replace(/(\w)(\d+)/g, (_, letter, num) => {
    return letter + num.split('').map((d: string) => subscripts[d] || d).join('');
  });
}

/**
 * Detect LaTeX commands and common bare subscript/superscript forms.
 * This is used for dedicated equation blocks only; Markdown requires delimiters.
 */
function hasLatexNotation(text: string): boolean {
  return /\\[a-zA-Z]+|[_^](?:\{[^}]*\}|[A-Za-z0-9])/.test(text);
}

/**
 * Render LaTeX when requested or detected. Malformed input is returned as a
 * React text node, so it remains readable and cannot inject HTML.
 */
export function MathRenderer({
  children,
  displayMode = false,
  forceLatex = false,
}: MathRendererProps) {
  if (forceLatex || hasLatexNotation(children)) {
    const html = renderLatex(children, displayMode);

    if (html !== null) {
      return (
        <span
          className="katex-wrapper"
          dangerouslySetInnerHTML={{ __html: html }}
        />
      );
    }

    return <span className="katex-fallback">{children}</span>;
  }

  return <span>{convertAsciiSubscripts(children)}</span>;
}
