'use client';

import { useEffect, useRef } from 'react';

interface HelpDialogProps {
  isOpen: boolean;
  onClose: () => void;
}

export function HelpDialog({ isOpen, onClose }: HelpDialogProps) {
  const dialogRef = useRef<HTMLDivElement>(null);

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

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center px-4">
      <div
        ref={dialogRef}
        className="w-full max-w-md bg-[var(--color-surface-elevated)] border border-[rgba(255,255,255,0.08)] rounded-lg shadow-2xl"
        role="dialog"
        aria-modal="true"
        aria-labelledby="help-dialog-title"
      >
        <div className="p-5 border-b border-[rgba(255,255,255,0.04)]">
          <div className="flex items-center justify-between">
            <h2 id="help-dialog-title" className="text-base font-semibold text-[var(--color-text-primary)]">
              How to use Adhyayan
            </h2>
            <button
              onClick={onClose}
              className="w-8 h-8 flex items-center justify-center rounded hover:bg-[var(--color-surface-raised)] transition-colors"
              aria-label="Close help dialog"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <div className="p-5 space-y-4">
          <ol className="space-y-3 text-[14px] leading-relaxed text-[var(--color-text-secondary)]">
            <li className="flex gap-3">
              <span className="font-medium text-[var(--color-accent)] flex-shrink-0">1.</span>
              <span>Choose a subject from the sidebar.</span>
            </li>
            <li className="flex gap-3">
              <span className="font-medium text-[var(--color-accent)] flex-shrink-0">2.</span>
              <span>Select a chapter to focus your learning.</span>
            </li>
            <li className="flex gap-3">
              <span className="font-medium text-[var(--color-accent)] flex-shrink-0">3.</span>
              <span>Ask a question about the chapter content.</span>
            </li>
            <li className="flex gap-3">
              <span className="font-medium text-[var(--color-accent)] flex-shrink-0">4.</span>
              <span>Use suggested questions to explore key concepts.</span>
            </li>
          </ol>

          <div className="pt-3 border-t border-[rgba(255,255,255,0.04)]">
            <p className="text-[13px] text-[var(--color-text-tertiary)] leading-relaxed">
              Answers are grounded in the NCERT chapters, helping you understand the curriculum deeply.
            </p>
          </div>
        </div>

        <div className="p-4 border-t border-[rgba(255,255,255,0.04)]">
          <button
            onClick={onClose}
            className="w-full px-4 py-2.5 bg-[var(--color-accent)] hover:bg-[var(--color-accent-hover)] text-white rounded-md text-sm font-medium transition-colors"
          >
            Got it
          </button>
        </div>
      </div>
    </div>
  );
}
