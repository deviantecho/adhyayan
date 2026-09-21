/**
 * Markdown renderer for assistant responses
 * Parses markdown syntax into formatted HTML
 * Phase 3.16J: Added table rendering support
 */

import React from 'react';

interface MarkdownRendererProps {
  content: string;
}

/**
 * Parse Markdown table into structured data
 */
function parseMarkdownTable(lines: string[], startIndex: number): {
  rows: string[][],
  endIndex: number
} | null {
  if (startIndex >= lines.length) return null;

  const rows: string[][] = [];
  let i = startIndex;

  // Check if this looks like a table (has pipes)
  if (!lines[i].includes('|')) return null;

  // Parse header row
  const headerCells = lines[i]
    .split('|')
    .map(cell => cell.trim())
    .filter(cell => cell.length > 0);

  if (headerCells.length === 0) return null;
  rows.push(headerCells);
  i++;

  // Check for separator row (e.g., |---|---|)
  if (i < lines.length && lines[i].includes('|') && lines[i].includes('-')) {
    i++; // Skip separator
  }

  // Parse data rows
  while (i < lines.length && lines[i].includes('|')) {
    const cells = lines[i]
      .split('|')
      .map(cell => cell.trim())
      .filter(cell => cell.length > 0);

    if (cells.length === 0) break;
    rows.push(cells);
    i++;
  }

  return rows.length > 1 ? { rows, endIndex: i } : null;
}

export function MarkdownRenderer({ content }: MarkdownRendererProps) {
  const renderContent = (text: string) => {
    const lines = text.split('\n');
    const elements: React.ReactElement[] = [];
    let currentList: string[] = [];
    let listType: 'ul' | 'ol' | null = null;
    let listKey = 0;
    let i = 0;

    const flushList = () => {
      if (currentList.length > 0 && listType) {
        const ListTag = listType;
        elements.push(
          <ListTag key={`list-${listKey++}`} className="space-y-2 my-4 pl-5">
            {currentList.map((item, idx) => (
              <li key={idx} className="text-answer-body leading-loose">
                {renderInline(item)}
              </li>
            ))}
          </ListTag>
        );
        currentList = [];
        listType = null;
      }
    };

    while (i < lines.length) {
      const line = lines[i];
      const trimmed = line.trim();

      if (!trimmed) {
        flushList();
        i++;
        continue;
      }

      // Check for table
      if (trimmed.includes('|')) {
        const tableData = parseMarkdownTable(lines, i);
        if (tableData) {
          flushList();
          const { rows, endIndex } = tableData;

          elements.push(
            <div key={`table-wrapper-${i}`} className="my-6 overflow-x-auto">
              <table className="min-w-full border-collapse bg-[rgba(255,255,255,0.01)] border border-[rgba(255,255,255,0.06)] rounded-lg overflow-hidden">
                <thead>
                  <tr className="bg-[rgba(255,255,255,0.03)] border-b border-[rgba(255,255,255,0.08)]">
                    {rows[0].map((cell, cellIdx) => (
                      <th
                        key={cellIdx}
                        className="px-4 py-3 text-left text-[13px] font-semibold tracking-wide text-[var(--color-text-secondary)] uppercase"
                      >
                        {renderInline(cell)}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {rows.slice(1).map((row, rowIdx) => (
                    <tr
                      key={rowIdx}
                      className="border-b border-[rgba(255,255,255,0.04)] last:border-b-0 hover:bg-[rgba(255,255,255,0.02)] transition-colors"
                    >
                      {row.map((cell, cellIdx) => (
                        <td
                          key={cellIdx}
                          className="px-4 py-3 text-[15px] text-[var(--color-text-primary)] leading-relaxed"
                        >
                          {renderInline(cell)}
                        </td>
                      ))}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          );

          i = endIndex;
          continue;
        }
      }

      // Unordered list
      const ulMatch = trimmed.match(/^[\*\-]\s+(.+)$/);
      if (ulMatch) {
        if (listType !== 'ul') {
          flushList();
          listType = 'ul';
        }
        currentList.push(ulMatch[1]);
        i++;
        continue;
      }

      // Ordered list
      const olMatch = trimmed.match(/^\d+\.\s+(.+)$/);
      if (olMatch) {
        if (listType !== 'ol') {
          flushList();
          listType = 'ol';
        }
        currentList.push(olMatch[1]);
        i++;
        continue;
      }

      // Heading
      const headingMatch = trimmed.match(/^(#{1,6})\s+(.+)$/);
      if (headingMatch) {
        flushList();
        const level = headingMatch[1].length;
        const text = headingMatch[2];
        const HeadingTag = `h${level}` as 'h1' | 'h2' | 'h3' | 'h4' | 'h5' | 'h6';
        elements.push(
          <HeadingTag
            key={`heading-${i}`}
            className={`font-semibold my-4 ${level === 1 ? 'text-xl' : level === 2 ? 'text-lg' : 'text-base'}`}
          >
            {renderInline(text)}
          </HeadingTag>
        );
        i++;
        continue;
      }

      // Regular paragraph
      flushList();
      if (trimmed) {
        elements.push(
          <p key={`p-${i}`} className="text-answer-body leading-loose mb-4">
            {renderInline(line)}
          </p>
        );
      }
      i++;
    }

    flushList();
    return elements;
  };

  const renderInline = (text: string) => {
    const parts: (string | React.ReactNode)[] = [];
    let remaining = text;
    let key = 0;

    while (remaining) {
      // Bold: **text** or __text__
      const boldMatch = remaining.match(/^()(.*?)(\*\*|__)(.+?)\3/);
      if (boldMatch) {
        if (boldMatch[2]) parts.push(boldMatch[2]);
        parts.push(<strong key={`bold-${key++}`}>{boldMatch[4]}</strong>);
        remaining = remaining.slice(boldMatch[0].length);
        continue;
      }

      // Italic: *text* or _text_ (handles *text:* correctly now)
      // Must check for asterisk NOT followed by another asterisk
      const italicMatch = remaining.match(/^()(.*?)(\*)([^*]+)\*/);
      if (italicMatch) {
        if (italicMatch[2]) parts.push(italicMatch[2]);
        parts.push(<em key={`italic-${key++}`}>{italicMatch[4]}</em>);
        remaining = remaining.slice(italicMatch[0].length);
        continue;
      }

      // Also handle underscore italic: _text_
      const italicUnderscoreMatch = remaining.match(/^()(.*?)(_)([^_]+)_/);
      if (italicUnderscoreMatch) {
        if (italicUnderscoreMatch[2]) parts.push(italicUnderscoreMatch[2]);
        parts.push(<em key={`italic-${key++}`}>{italicUnderscoreMatch[4]}</em>);
        remaining = remaining.slice(italicUnderscoreMatch[0].length);
        continue;
      }

      // Inline code: `code`
      const codeMatch = remaining.match(/^(.*?)`(.+?)`/);
      if (codeMatch) {
        if (codeMatch[1]) parts.push(codeMatch[1]);
        parts.push(
          <code
            key={`code-${key++}`}
            className="px-1.5 py-0.5 bg-[var(--color-surface)] rounded text-sm font-mono"
          >
            {codeMatch[2]}
          </code>
        );
        remaining = remaining.slice(codeMatch[0].length);
        continue;
      }

      // No more matches, add remaining text
      parts.push(remaining);
      break;
    }

    return parts;
  };

  return <div className="space-y-2">{renderContent(content)}</div>;
}
