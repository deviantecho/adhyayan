/**
 * Markdown renderer for assistant responses
 * Parses markdown syntax into formatted HTML
 */

import React from 'react';

interface MarkdownRendererProps {
  content: string;
}

export function MarkdownRenderer({ content }: MarkdownRendererProps) {
  const renderContent = (text: string) => {
    const lines = text.split('\n');
    const elements: React.ReactElement[] = [];
    let currentList: string[] = [];
    let listType: 'ul' | 'ol' | null = null;
    let listKey = 0;

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

    for (let i = 0; i < lines.length; i++) {
      const line = lines[i];
      const trimmed = line.trim();

      if (!trimmed) {
        flushList();
        continue;
      }

      // Unordered list
      const ulMatch = trimmed.match(/^[\*\-]\s+(.+)$/);
      if (ulMatch) {
        if (listType !== 'ul') {
          flushList();
          listType = 'ul';
        }
        currentList.push(ulMatch[1]);
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
    }

    flushList();
    return elements;
  };

  const renderInline = (text: string) => {
    const parts: (string | React.ReactElement)[] = [];
    let remaining = text;
    let key = 0;

    while (remaining) {
      // Bold: **text** or __text__
      const boldMatch = remaining.match(/^(.*?)(\*\*|__)(.+?)\2/);
      if (boldMatch) {
        if (boldMatch[1]) parts.push(boldMatch[1]);
        parts.push(<strong key={`bold-${key++}`}>{boldMatch[3]}</strong>);
        remaining = remaining.slice(boldMatch[0].length);
        continue;
      }

      // Italic: *text* or _text_
      const italicMatch = remaining.match(/^(.*?)(\*|_)(.+?)\2/);
      if (italicMatch) {
        if (italicMatch[1]) parts.push(italicMatch[1]);
        parts.push(<em key={`italic-${key++}`}>{italicMatch[3]}</em>);
        remaining = remaining.slice(italicMatch[0].length);
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
