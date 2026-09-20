'use client';

import { useState, useRef, useEffect } from 'react';
import { chat, type Message as APIMessage, type ChatResponse } from '@/lib/api';
import { SUBJECTS, getSubject, getChapter, type Chapter } from '@/lib/curriculum-data';
import { ChapterHero } from '@/components/ChapterHero';
import { SearchDialog } from '@/components/SearchDialog';
import { HelpDialog } from '@/components/HelpDialog';
import { AboutDialog } from '@/components/AboutDialog';
import { StructuredAnswer } from '@/components/StructuredAnswer';
import { UserAvatar } from '@/components/UserAvatar';
import { getHeroAssets } from '@/lib/hero-assets';

interface Message extends APIMessage {
  sources?: string[];
  retrievalDetails?: Array<{
    rank: number;
    subject: string;
    chapter: string;
    section: string;
    distance: number;
  }>;
}

type ViewMode = 'overview' | 'chapter';
type SubjectId = 'science' | 'mathematics';

export default function Home() {
  // Navigation state
  const [viewMode, setViewMode] = useState<ViewMode>('chapter');
  const [currentSubject, setCurrentSubject] = useState<SubjectId>('science');
  const [currentChapterId, setCurrentChapterId] = useState<string>('chapter1');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  // Dialog state
  const [isSearchOpen, setIsSearchOpen] = useState(false);
  const [isHelpOpen, setIsHelpOpen] = useState(false);
  const [isAboutOpen, setIsAboutOpen] = useState(false);

  // Chat state
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Cmd/Ctrl + K for search
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setIsSearchOpen(true);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  const currentChapter = getChapter(currentSubject, currentChapterId);
  const currentSubjectData = getSubject(currentSubject);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      role: 'user',
      content: input.trim(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response: ChatResponse = await chat({
        message: userMessage.content,
        chat_history: messages.map(m => ({ role: m.role, content: m.content })),
        subject_filter: currentSubject === 'science' ? 'Science' : 'Mathematics',
        stream: false,
      });

      const assistantMessage: Message = {
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
        retrievalDetails: response.retrieval_details,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Chat error:', error);

      let userMessage = 'The tutor is temporarily unavailable. Please try again in a few moments.';

      if (error instanceof Error) {
        const errorText = error.message.toLowerCase();
        if (errorText.includes('quota') || errorText.includes('429') || errorText.includes('resource_exhausted')) {
          userMessage = 'The tutor has reached its current usage limit. Please try again later.';
        } else if (errorText.includes('network') || errorText.includes('fetch')) {
          userMessage = 'Unable to connect to the tutor. Please check your connection and try again.';
        }
      }

      const errorMessage: Message = {
        role: 'assistant',
        content: userMessage,
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNewChat = () => {
    setMessages([]);
    setInput('');
  };

  const handleOverviewClick = () => {
    setViewMode('overview');
    setMessages([]);
  };

  const handleSubjectClick = (subjectId: SubjectId) => {
    setCurrentSubject(subjectId);
    setViewMode('chapter');
    const firstChapter = getSubject(subjectId)?.chapters[0];
    if (firstChapter) {
      setCurrentChapterId(firstChapter.id);
    }
    setMessages([]);
    setIsSidebarOpen(false);
  };

  const handleChapterClick = (chapterId: string) => {
    setCurrentChapterId(chapterId);
    setViewMode('chapter');
    setMessages([]);
    setIsSidebarOpen(false);
  };

  const handleSearchSelect = (subjectId: SubjectId, chapterId: string) => {
    setCurrentSubject(subjectId);
    setCurrentChapterId(chapterId);
    setViewMode('chapter');
    setMessages([]);
  };

  return (
    <div className="flex h-screen bg-[var(--color-background)]">
      {/* Search Dialog */}
      <SearchDialog
        isOpen={isSearchOpen}
        onClose={() => setIsSearchOpen(false)}
        onSelectChapter={handleSearchSelect}
      />

      {/* Help Dialog */}
      <HelpDialog isOpen={isHelpOpen} onClose={() => setIsHelpOpen(false)} />
      {/* About Dialog */}
      <AboutDialog isOpen={isAboutOpen} onClose={() => setIsAboutOpen(false)} />
      {/* Sidebar - Desktop */}
      <aside className="hidden lg:flex lg:flex-col w-64 border-r border-[rgba(255,255,255,0.04)] bg-[var(--color-background)]">
        <div className="p-5">
          <div className="flex items-center gap-3 mb-6">
            <div className="w-9 h-9 bg-[var(--color-accent)] rounded-md flex items-center justify-center flex-shrink-0">
              <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <div className="min-w-0">
              <div className="font-semibold text-sm leading-tight tracking-tight">Adhyayan</div>
              <div className="text-xs text-[var(--color-text-secondary)] leading-tight">Class 10 NCERT Study Companion</div>
            </div>
          </div>

          <button
            onClick={handleNewChat}
            className="w-full px-4 py-2.5 bg-[var(--color-accent)] hover:bg-[var(--color-accent-hover)] text-white rounded-md text-sm font-medium transition-colors"
          >
            + New Chat
          </button>
        </div>

        <nav className="flex-1 px-2.5 overflow-y-auto">
          <div className="text-label text-[var(--color-text-tertiary)] px-3 mb-2.5">Learn</div>

          <button
            onClick={handleOverviewClick}
            className={`nav-item ${viewMode === 'overview' ? 'active' : ''}`}
          >
            <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            Overview
          </button>

          <button
            onClick={() => handleSubjectClick('science')}
            className={`nav-item ${currentSubject === 'science' && viewMode === 'chapter' ? 'active' : ''}`}
          >
            <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 008 10.172V5L7 4z" />
            </svg>
            Science
          </button>

          <button
            onClick={() => handleSubjectClick('mathematics')}
            className={`nav-item ${currentSubject === 'mathematics' && viewMode === 'chapter' ? 'active' : ''}`}
          >
            <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
            Mathematics
          </button>

          {currentSubjectData && viewMode === 'chapter' && (
            <>
              <div className="text-label text-[var(--color-text-tertiary)] px-3 mb-2.5 mt-6">
                {currentSubjectData.name}
              </div>
              {currentSubjectData.chapters.map((chapter) => (
                <button
                  key={chapter.id}
                  onClick={() => handleChapterClick(chapter.id)}
                  className={`nav-item ${currentChapterId === chapter.id ? 'active' : ''}`}
                >
                  <span className="text-xs text-[var(--color-text-tertiary)] font-medium flex-shrink-0 w-6">
                    {String(chapter.number).padStart(2, '0')}
                  </span>
                  <span className="truncate text-left text-[13px]">{chapter.title}</span>
                </button>
              ))}
            </>
          )}
        </nav>

        <div className="p-2.5 border-t border-[rgba(255,255,255,0.04)]">
          <button className="nav-item" onClick={() => setIsHelpOpen(true)}>
            <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Help
          </button>
          <button className="nav-item" onClick={() => setIsAboutOpen(true)}>
            <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            About
          </button>
        </div>
      </aside>

      {/* Mobile Sidebar Overlay */}
      {isSidebarOpen && (
        <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" onClick={() => setIsSidebarOpen(false)} />
      )}

      {/* Mobile Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 w-64 border-r border-[rgba(255,255,255,0.04)] bg-[var(--color-background)] z-50 lg:hidden transform transition-transform ${
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex flex-col h-full">
          <div className="p-5">
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-3">
                <div className="w-9 h-9 bg-[var(--color-accent)] rounded-md flex items-center justify-center">
                  <svg className="w-5 h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                </div>
                <div>
                  <div className="font-semibold text-sm">Adhyayan</div>
                  <div className="text-xs text-[var(--color-text-secondary)]">Class 10 NCERT Study Companion</div>
                </div>
              </div>
              <button onClick={() => setIsSidebarOpen(false)} className="p-1">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <button
              onClick={() => {
                handleNewChat();
                setIsSidebarOpen(false);
              }}
              className="w-full px-4 py-2.5 bg-[var(--color-accent)] hover:bg-[var(--color-accent-hover)] text-white rounded-md text-sm font-medium transition-colors"
            >
              + New Chat
            </button>
          </div>

          <nav className="flex-1 px-2.5 overflow-y-auto">
            <div className="text-label text-[var(--color-text-tertiary)] px-3 mb-2.5">Learn</div>

            <button
              onClick={handleOverviewClick}
              className={`nav-item ${viewMode === 'overview' ? 'active' : ''}`}
            >
              <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              Overview
            </button>

            <button
              onClick={() => handleSubjectClick('science')}
              className={`nav-item ${currentSubject === 'science' && viewMode === 'chapter' ? 'active' : ''}`}
            >
              <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 008 10.172V5L7 4z" />
              </svg>
              Science
            </button>

            <button
              onClick={() => handleSubjectClick('mathematics')}
              className={`nav-item ${currentSubject === 'mathematics' && viewMode === 'chapter' ? 'active' : ''}`}
            >
              <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              Mathematics
            </button>

            {currentSubjectData && viewMode === 'chapter' && (
              <>
                <div className="text-label text-[var(--color-text-tertiary)] px-3 mb-2.5 mt-6">
                  {currentSubjectData.name}
                </div>
                {currentSubjectData.chapters.map((chapter) => (
                  <button
                    key={chapter.id}
                    onClick={() => handleChapterClick(chapter.id)}
                    className={`nav-item ${currentChapterId === chapter.id ? 'active' : ''}`}
                  >
                    <span className="text-xs text-[var(--color-text-tertiary)] font-medium flex-shrink-0 w-6">
                      {String(chapter.number).padStart(2, '0')}
                    </span>
                    <span className="truncate text-left text-[13px]">{chapter.title}</span>
                  </button>
                ))}
              </>
            )}
          </nav>

          <div className="p-2.5 border-t border-[rgba(255,255,255,0.04)]">
            <button className="nav-item" onClick={() => { setIsHelpOpen(true); setIsSidebarOpen(false); }}>
              <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Help
            </button>
            <button className="nav-item" onClick={() => { setIsAboutOpen(true); setIsSidebarOpen(false); }}>
              <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              About
            </button>
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="border-b border-[rgba(255,255,255,0.04)] bg-[var(--color-background)] flex-shrink-0">
          <div className="flex items-center justify-between gap-4 px-4 lg:px-6 py-3">
            <div className="flex items-center gap-4 min-w-0 flex-1">
              <button className="lg:hidden flex-shrink-0" onClick={() => setIsSidebarOpen(true)}>
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              {viewMode === 'chapter' && currentChapter && (
                <div className="hidden md:flex items-center gap-2 text-[13px] text-[var(--color-text-secondary)] overflow-hidden">
                  <button
                    onClick={() => handleSubjectClick(currentSubject)}
                    className="truncate hover:text-[var(--color-text-primary)] transition-colors"
                  >
                    {currentSubjectData?.name}
                  </button>
                  <svg className="w-3.5 h-3.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                  <button
                    onClick={() => handleChapterClick(currentChapterId)}
                    className="truncate hover:text-[var(--color-text-primary)] transition-colors"
                  >
                    Chapter {currentChapter.number}
                  </button>
                  <svg className="w-3.5 h-3.5 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                  <span className="text-[var(--color-text-primary)] truncate">{currentChapter.title}</span>
                </div>
              )}
              {viewMode === 'overview' && (
                <div className="hidden md:block text-[13px] font-medium">Curriculum Overview</div>
              )}
              <div className="md:hidden text-[13px] font-medium truncate">Adhyayan</div>
            </div>
            <div className="flex items-center gap-3 flex-shrink-0">
              <button
                onClick={() => setIsSearchOpen(true)}
                className="hidden lg:flex search-field w-72"
              >
                <svg className="w-3.5 h-3.5 text-[var(--color-text-tertiary)]" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
                <span className="flex-1 text-left text-[13px] text-[var(--color-text-tertiary)]">
                  Search chapters, concepts...
                </span>
                <kbd>⌘K</kbd>
              </button>
              <UserAvatar size="md" initial="D" />
            </div>
          </div>
        </header>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto">
          {viewMode === 'overview' ? (
            <div className="max-w-3xl mx-auto px-4 lg:px-6 py-6 lg:py-8">
              <div className="py-8 lg:py-12">
              <div className="mb-16">
                <h1 className="text-display mb-3">Adhyayan</h1>
                <div className="text-lg text-[var(--color-text-secondary)] mb-6">Class 10 NCERT Study Companion</div>
                <p className="text-body text-[var(--color-text-secondary)] max-w-xl leading-relaxed">
                  A guided path through Science and Mathematics. Choose your chapter and begin exploring.
                </p>
              </div>

              <div className="space-y-16">
                {SUBJECTS.map((subject) => (
                  <section key={subject.id}>
                    <div className="mb-8">
                      <button
                        onClick={() => handleSubjectClick(subject.id)}
                        className="inline-block mb-3 text-heading hover:text-[var(--color-accent)] transition-colors cursor-pointer"
                      >
                        {subject.name}
                      </button>
                      <div className="flex items-baseline gap-3 mb-3">
                        <span className="text-sm text-[var(--color-text-tertiary)] uppercase tracking-wide">
                          {subject.chapters.length} Chapters
                        </span>
                      </div>
                      <p className="text-body text-[var(--color-text-secondary)] leading-relaxed max-w-2xl">
                        {subject.description}
                      </p>
                    </div>

                    <div className="space-y-2">
                      {subject.chapters.map((chapter) => (
                        <button
                          key={chapter.id}
                          onClick={() => {
                            handleSubjectClick(subject.id);
                            handleChapterClick(chapter.id);
                          }}
                          className="overview-chapter-row"
                        >
                          <span className="chapter-number">
                            {String(chapter.number).padStart(2, '0')}
                          </span>
                          <div className="chapter-info">
                            <h3 className="chapter-title">
                              {chapter.title}
                            </h3>
                            <p className="chapter-description">
                              {chapter.description}
                            </p>
                          </div>
                          <svg className="chapter-arrow" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                        </button>
                      ))}
                    </div>
                  </section>
                ))}
              </div>
            </div>
            </div>
          ) : currentChapter ? (
            <>
              {/* Chapter Hero - Always visible */}
              <ChapterHero
                subject={currentSubject}
                chapterNumber={currentChapter.number}
                title={currentChapter.title}
                description={currentChapter.description}
                heroImage={getHeroAssets(currentSubject).image}
                compact={messages.length > 0}
              />

              <div className="learning-canvas">
                {messages.length === 0 ? (
                  <div className="py-4 lg:py-6">
                    <div className="suggested-questions-grid">
                      {currentChapter.suggestedQuestions.map((question, idx) => (
                        <button
                          key={idx}
                          onClick={() => setInput(question)}
                          className="suggested-question-card"
                        >
                          <div className="text">{question}</div>
                          <svg className="arrow" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                          </svg>
                        </button>
                      ))}
                    </div>
                  </div>
                ) : (
                  <div className="py-4 lg:py-6 space-y-6 lg:space-y-7">
                    {messages.map((message, idx) => (
                      <div key={idx}>
                        {message.role === 'user' ? (
                          <div className="flex items-start gap-3">
                            <UserAvatar size="sm" initial="D" />
                            <div className="flex-1 min-w-0">
                              <div className="bg-[var(--color-accent-bg)] border border-[rgba(13,155,129,0.15)] rounded-md px-3 py-2.5 inline-block max-w-full">
                                <p className="text-[14px] break-words leading-relaxed">{message.content}</p>
                              </div>
                            </div>
                          </div>
                        ) : (
                          <div className="flex items-start gap-3">
                            <div className="w-8 h-8 rounded-full bg-[var(--color-accent)] flex items-center justify-center flex-shrink-0">
                              <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                              </svg>
                            </div>
                            <div className="flex-1 min-w-0 answer-content">
                              <StructuredAnswer
                                content={message.content}
                                sources={message.sources}
                                retrievalDetails={message.retrievalDetails}
                              />
                            </div>
                          </div>
                        )}
                      </div>
                    ))}
                    {isLoading && (
                      <div className="flex items-start gap-3">
                        <div className="w-8 h-8 rounded-full bg-[var(--color-accent)] flex items-center justify-center flex-shrink-0">
                          <svg className="w-4 h-4 text-white animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                          </svg>
                        </div>
                        <div className="text-[14px] text-[var(--color-text-secondary)]">Searching chapters...</div>
                      </div>
                    )}
                    <div ref={messagesEndRef} />
                  </div>
                )}
              </div>
            </>
          ) : null}
        </div>

        {/* Composer - Only show in chapter view */}
        {viewMode === 'chapter' && (
          <div className="composer-container">
            <div className="composer-wrapper">
              <form onSubmit={handleSubmit} className="composer-form">
                <div className="composer-field-wrapper">
                  <div className="composer-input-container">
                    <textarea
                      value={input}
                      onChange={(e) => setInput(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter' && !e.shiftKey) {
                          e.preventDefault();
                          handleSubmit(e);
                        }
                      }}
                      placeholder="Ask a question about this chapter..."
                      rows={1}
                      className="composer-input"
                    />
                    <button
                      type="submit"
                      disabled={!input.trim() || isLoading}
                      className="composer-submit"
                    >
                      <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                      </svg>
                    </button>
                  </div>
                  {currentChapter && (
                    <div className="composer-context">
                      <span>{currentSubjectData?.name} · Chapter {currentChapter.number}</span>
                    </div>
                  )}
                </div>
              </form>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}
