'use client';

import { useState, useEffect, useRef } from 'react';
import { SUBJECTS, type Chapter, type Subject } from '@/lib/curriculum-data';

interface SearchResult {
  subject: Subject;
  chapter: Chapter;
}

interface SearchDialogProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectChapter: (subjectId: 'science' | 'mathematics', chapterId: string) => void;
}

export function SearchDialog({ isOpen, onClose, onSelectChapter }: SearchDialogProps) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const inputRef = useRef<HTMLInputElement>(null);
  const dialogRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (isOpen) {
      inputRef.current?.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    const handleClickOutside = (e: MouseEvent) => {
      if (dialogRef.current && !dialogRef.current.contains(e.target as Node)) {
        onClose();
      }
    };

    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
      document.addEventListener('keydown', handleEscape);
    }

    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
      document.removeEventListener('keydown', handleEscape);
    };
  }, [isOpen, onClose]);

  useEffect(() => {
    if (!query.trim()) {
      setResults([]);
      return;
    }

    const searchQuery = query.toLowerCase();
    const matches: SearchResult[] = [];

    for (const subject of SUBJECTS) {
      // Search subject name
      if (subject.name.toLowerCase().includes(searchQuery)) {
        // Add all chapters if subject matches
        subject.chapters.forEach(chapter => {
          matches.push({ subject, chapter });
        });
        continue;
      }

      // Search individual chapters
      for (const chapter of subject.chapters) {
        const matchesChapter =
          chapter.title.toLowerCase().includes(searchQuery) ||
          chapter.description.toLowerCase().includes(searchQuery) ||
          chapter.number.toString().includes(searchQuery);

        if (matchesChapter) {
          matches.push({ subject, chapter });
        }
      }
    }

    setResults(matches.slice(0, 8)); // Limit to 8 results
  }, [query]);

  const handleSelect = (subjectId: 'science' | 'mathematics', chapterId: string) => {
    onSelectChapter(subjectId, chapterId);
    setQuery('');
    setResults([]);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-start justify-center pt-20 lg:pt-32 px-4">
      <div
        ref={dialogRef}
        className="w-full max-w-2xl bg-[var(--color-surface-elevated)] border border-[rgba(255,255,255,0.08)] rounded-lg shadow-2xl"
        role="dialog"
        aria-modal="true"
        aria-label="Search chapters"
      >
        <div className="p-4 border-b border-[rgba(255,255,255,0.04)]">
          <div className="flex items-center gap-3">
            <svg className="w-5 h-5 text-[var(--color-text-tertiary)] flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            <input
              ref={inputRef}
              type="text"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Search chapters, concepts, or questions..."
              className="flex-1 bg-transparent border-none outline-none text-[15px] text-[var(--color-text-primary)]"
              aria-label="Search input"
            />
            <kbd className="hidden lg:block px-2 py-1 bg-[var(--color-background)] border border-[rgba(255,255,255,0.04)] rounded text-xs text-[var(--color-text-tertiary)]">
              ESC
            </kbd>
          </div>
        </div>

        {results.length > 0 && (
          <div className="max-h-96 overflow-y-auto">
            {results.map((result, idx) => (
              <button
                key={`${result.subject.id}-${result.chapter.id}-${idx}`}
                onClick={() => handleSelect(result.subject.id, result.chapter.id)}
                className="w-full px-4 py-3 text-left hover:bg-[var(--color-surface-raised)] transition-colors border-b border-[rgba(255,255,255,0.02)] last:border-b-0"
              >
                <div className="flex items-start gap-3">
                  <span className="text-xs text-[var(--color-text-tertiary)] font-medium mt-1 flex-shrink-0">
                    {String(result.chapter.number).padStart(2, '0')}
                  </span>
                  <div className="flex-1 min-w-0">
                    <div className="text-[13px] font-medium text-[var(--color-text-primary)] mb-0.5">
                      {result.chapter.title}
                    </div>
                    <div className="text-xs text-[var(--color-text-tertiary)]">
                      {result.subject.name} · Chapter {result.chapter.number}
                    </div>
                  </div>
                </div>
              </button>
            ))}
          </div>
        )}

        {query.trim() && results.length === 0 && (
          <div className="p-8 text-center text-[13px] text-[var(--color-text-tertiary)]">
            No chapters found matching &ldquo;{query}&rdquo;
          </div>
        )}

        {!query.trim() && (
          <div className="p-8 text-center text-[13px] text-[var(--color-text-tertiary)]">
            Start typing to search chapters...
          </div>
        )}
      </div>
    </div>
  );
}
