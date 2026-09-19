'use client';

import { useState, useRef, useEffect } from 'react';
import { chat, type Message as APIMessage, type ChatResponse } from '@/lib/api';
import { SUBJECTS, getSubject, getChapter, type Chapter } from '@/lib/curriculum-data';

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

      // Provide user-friendly error message
      let userMessage = 'The tutor is temporarily unavailable. Please try again later.';

      if (error instanceof Error) {
        const errorText = error.message.toLowerCase();
        if (errorText.includes('quota') || errorText.includes('429') || errorText.includes('resource_exhausted')) {
          userMessage = 'The tutor is currently at capacity. Please try again in a few moments.';
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

  const extractKeyIdea = (content: string): { keyIdea: string; rest: string } | null => {
    const lines = content.split('\n');
    let keyIdeaStart = -1;

    for (let i = 0; i < lines.length; i++) {
      if (lines[i].includes('Key Idea') || lines[i].includes('KEY IDEA')) {
        keyIdeaStart = i;
        break;
      }
    }

    if (keyIdeaStart >= 0 && keyIdeaStart < lines.length - 1) {
      const keyIdea = lines.slice(keyIdeaStart + 1, keyIdeaStart + 2).join('\n').trim();
      const rest = [...lines.slice(0, keyIdeaStart), ...lines.slice(keyIdeaStart + 2)].join('\n').trim();
      return { keyIdea, rest };
    }

    return null;
  };

  return (
    <div className="flex h-screen bg-[var(--color-background)]">
      {/* Sidebar - Desktop */}
      <aside className="hidden lg:flex lg:flex-col w-64 border-r border-[var(--color-border)] bg-[var(--color-background)]">
        <div className="p-6">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-[var(--color-accent)] rounded-lg flex items-center justify-center">
              <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <div>
              <div className="font-semibold text-sm">NCERT</div>
              <div className="text-xs text-[var(--color-text-secondary)]">Study Companion</div>
              <div className="text-[10px] text-[var(--color-text-tertiary)]">Class 10</div>
            </div>
          </div>

          <button
            onClick={handleNewChat}
            className="w-full px-4 py-2.5 bg-[var(--color-accent)] hover:bg-[var(--color-accent-hover)] text-white rounded-lg text-sm font-medium transition-colors"
          >
            + New Chat
          </button>
        </div>

        <nav className="flex-1 px-3 overflow-y-auto">
          <div className="text-xs font-medium text-[var(--color-text-tertiary)] px-3 mb-2">Learn</div>
          <button
            onClick={handleOverviewClick}
            className={`w-full flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition-colors ${
              viewMode === 'overview'
                ? 'text-[var(--color-text-primary)] bg-[var(--color-surface)]'
                : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-surface)]'
            }`}
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
            </svg>
            Overview
          </button>
          <button
            onClick={() => handleSubjectClick('science')}
            className={`w-full flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition-colors ${
              currentSubject === 'science' && viewMode === 'chapter'
                ? 'text-[var(--color-text-primary)] bg-[var(--color-surface)]'
                : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-surface)]'
            }`}
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 008 10.172V5L7 4z" />
            </svg>
            Science
          </button>
          <button
            onClick={() => handleSubjectClick('mathematics')}
            className={`w-full flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition-colors ${
              currentSubject === 'mathematics' && viewMode === 'chapter'
                ? 'text-[var(--color-text-primary)] bg-[var(--color-surface)]'
                : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-surface)]'
            }`}
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
            </svg>
            Mathematics
          </button>

          {currentSubjectData && viewMode === 'chapter' && (
            <>
              <div className="text-xs font-medium text-[var(--color-text-tertiary)] px-3 mb-2 mt-6">
                {currentSubjectData.name} Chapters
              </div>
              {currentSubjectData.chapters.map((chapter) => (
                <button
                  key={chapter.id}
                  onClick={() => handleChapterClick(chapter.id)}
                  className={`w-full flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition-colors ${
                    currentChapterId === chapter.id
                      ? 'text-[var(--color-text-primary)] bg-[var(--color-surface)]'
                      : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-surface)]'
                  }`}
                >
                  <span className="text-xs text-[var(--color-text-tertiary)] flex-shrink-0">
                    {String(chapter.number).padStart(2, '0')}
                  </span>
                  <span className="truncate text-left">{chapter.title}</span>
                </button>
              ))}
            </>
          )}
        </nav>

        <div className="p-3 border-t border-[var(--color-border)]">
          <button className="w-full flex items-center gap-3 px-3 py-2 text-sm text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-surface)] rounded-lg transition-colors">
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            Help
          </button>
        </div>
      </aside>

      {/* Mobile Sidebar Overlay */}
      {isSidebarOpen && (
        <div className="fixed inset-0 bg-black/50 z-40 lg:hidden" onClick={() => setIsSidebarOpen(false)} />
      )}

      {/* Mobile Sidebar */}
      <aside
        className={`fixed inset-y-0 left-0 w-64 border-r border-[var(--color-border)] bg-[var(--color-background)] z-50 lg:hidden transform transition-transform ${
          isSidebarOpen ? 'translate-x-0' : '-translate-x-full'
        }`}
      >
        <div className="flex flex-col h-full">
          <div className="p-6">
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-[var(--color-accent)] rounded-lg flex items-center justify-center">
                  <svg className="w-6 h-6 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                  </svg>
                </div>
                <div>
                  <div className="font-semibold text-sm">NCERT</div>
                  <div className="text-xs text-[var(--color-text-secondary)]">Study Companion</div>
                </div>
              </div>
              <button onClick={() => setIsSidebarOpen(false)}>
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <button
              onClick={() => {
                handleNewChat();
                setIsSidebarOpen(false);
              }}
              className="w-full px-4 py-2.5 bg-[var(--color-accent)] hover:bg-[var(--color-accent-hover)] text-white rounded-lg text-sm font-medium transition-colors"
            >
              + New Chat
            </button>
          </div>

          <nav className="flex-1 px-3 overflow-y-auto">
            <div className="text-xs font-medium text-[var(--color-text-tertiary)] px-3 mb-2">Learn</div>
            <button
              onClick={handleOverviewClick}
              className={`w-full flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition-colors ${
                viewMode === 'overview'
                  ? 'text-[var(--color-text-primary)] bg-[var(--color-surface)]'
                  : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-surface)]'
              }`}
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              Overview
            </button>
            <button
              onClick={() => handleSubjectClick('science')}
              className={`w-full flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition-colors ${
                currentSubject === 'science' && viewMode === 'chapter'
                  ? 'text-[var(--color-text-primary)] bg-[var(--color-surface)]'
                  : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-surface)]'
              }`}
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 008 10.172V5L7 4z" />
              </svg>
              Science
            </button>
            <button
              onClick={() => handleSubjectClick('mathematics')}
              className={`w-full flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition-colors ${
                currentSubject === 'mathematics' && viewMode === 'chapter'
                  ? 'text-[var(--color-text-primary)] bg-[var(--color-surface)]'
                  : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-surface)]'
              }`}
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 7h6m0 10v-3m-3 3h.01M9 17h.01M9 14h.01M12 14h.01M15 11h.01M12 11h.01M9 11h.01M7 21h10a2 2 0 002-2V5a2 2 0 00-2-2H7a2 2 0 00-2 2v14a2 2 0 002 2z" />
              </svg>
              Mathematics
            </button>

            {currentSubjectData && viewMode === 'chapter' && (
              <>
                <div className="text-xs font-medium text-[var(--color-text-tertiary)] px-3 mb-2 mt-6">
                  {currentSubjectData.name} Chapters
                </div>
                {currentSubjectData.chapters.map((chapter) => (
                  <button
                    key={chapter.id}
                    onClick={() => handleChapterClick(chapter.id)}
                    className={`w-full flex items-center gap-3 px-3 py-2 text-sm rounded-lg transition-colors ${
                      currentChapterId === chapter.id
                        ? 'text-[var(--color-text-primary)] bg-[var(--color-surface)]'
                        : 'text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-surface)]'
                    }`}
                  >
                    <span className="text-xs text-[var(--color-text-tertiary)] flex-shrink-0">
                      {String(chapter.number).padStart(2, '0')}
                    </span>
                    <span className="truncate text-left">{chapter.title}</span>
                  </button>
                ))}
              </>
            )}
          </nav>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col min-w-0">
        {/* Header */}
        <header className="border-b border-[var(--color-border)] bg-[var(--color-background)] flex-shrink-0">
          <div className="flex items-center justify-between px-4 lg:px-6 py-4">
            <div className="flex items-center gap-4 min-w-0 flex-1">
              <button className="lg:hidden flex-shrink-0" onClick={() => setIsSidebarOpen(true)}>
                <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              </button>
              {viewMode === 'chapter' && currentChapter && (
                <div className="hidden md:flex items-center gap-2 text-sm text-[var(--color-text-secondary)] overflow-hidden">
                  <span className="truncate">{currentSubjectData?.name}</span>
                  <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                  <span className="truncate">Chapter {currentChapter.number}</span>
                  <svg className="w-4 h-4 flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                  </svg>
                  <span className="text-[var(--color-text-primary)] truncate">{currentChapter.title}</span>
                </div>
              )}
              {viewMode === 'overview' && (
                <div className="hidden md:block text-sm font-medium">Curriculum Overview</div>
              )}
              <div className="md:hidden text-sm font-medium truncate">NCERT Study Companion</div>
            </div>
            <div className="flex items-center gap-3 flex-shrink-0">
              <button className="p-2 hover:bg-[var(--color-surface)] rounded-lg transition-colors hidden md:block">
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </button>
              <div className="w-8 h-8 rounded-full bg-[var(--color-surface)] flex items-center justify-center text-sm font-medium">
                D
              </div>
            </div>
          </div>
        </header>

        {/* Content Area */}
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-3xl mx-auto px-4 lg:px-6 py-6 lg:py-8">
            {viewMode === 'overview' ? (
              <div className="py-8">
                <h1 className="text-display mb-6">NCERT Class 10</h1>
                <p className="text-body text-[var(--color-text-secondary)] mb-12 max-w-2xl">
                  Explore the complete curriculum for Science and Mathematics. Select a subject and chapter to begin your learning journey.
                </p>

                <div className="space-y-12">
                  {SUBJECTS.map((subject) => (
                    <div key={subject.id}>
                      <div className="mb-6">
                        <h2 className="text-heading mb-2">{subject.name}</h2>
                        <p className="text-body text-[var(--color-text-secondary)]">{subject.description}</p>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {subject.chapters.map((chapter) => (
                          <button
                            key={chapter.id}
                            onClick={() => {
                              handleSubjectClick(subject.id);
                              handleChapterClick(chapter.id);
                            }}
                            className="p-4 text-left bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg hover:border-[var(--color-accent)] transition-colors group"
                          >
                            <div className="flex items-start gap-3 mb-2">
                              <span className="text-xs text-[var(--color-text-tertiary)] font-medium">
                                {String(chapter.number).padStart(2, '0')}
                              </span>
                              <h3 className="text-sm font-medium text-[var(--color-text-primary)] group-hover:text-[var(--color-accent)] transition-colors flex-1">
                                {chapter.title}
                              </h3>
                            </div>
                            <p className="text-sm text-[var(--color-text-secondary)] ml-7">{chapter.description}</p>
                          </button>
                        ))}
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            ) : messages.length === 0 && currentChapter ? (
              <div className="py-8 lg:py-12">
                {/* Chapter Hero */}
                <div className="relative mb-12 pb-8 border-b border-[var(--color-border-subtle)]">
                  <div className="text-xs lg:text-sm font-medium text-[var(--color-accent)] mb-3 tracking-wide uppercase">
                    Chapter {currentChapter.number}
                  </div>
                  <h1 className="text-display mb-4 text-[var(--color-text-primary)]">
                    {currentChapter.title}
                  </h1>
                  <p className="text-body text-[var(--color-text-secondary)] leading-relaxed max-w-2xl">
                    {currentChapter.description}
                  </p>
                </div>

                <div className="mb-8 lg:mb-10">
                  <div className="text-sm font-medium text-[var(--color-text-tertiary)] mb-4">Explore this chapter</div>
                  <div className="space-y-3 max-w-2xl">
                    {currentChapter.suggestedQuestions.map((question, idx) => (
                      <button
                        key={idx}
                        onClick={() => setInput(question)}
                        className="w-full p-4 text-left bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg hover:border-[var(--color-accent)] transition-colors group"
                      >
                        <div className="text-sm lg:text-base text-[var(--color-text-primary)] group-hover:text-[var(--color-accent)] transition-colors">
                          {question}
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-6 lg:space-y-8">
                {messages.map((message, idx) => (
                  <div key={idx}>
                    {message.role === 'user' ? (
                      <div className="flex items-start gap-3 lg:gap-4">
                        <div className="w-7 h-7 lg:w-8 lg:h-8 rounded-full bg-[var(--color-surface)] flex items-center justify-center text-xs lg:text-sm font-medium flex-shrink-0">
                          D
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="bg-[var(--color-accent-bg)] border border-[var(--color-accent)]/20 rounded-lg px-3 lg:px-4 py-2 lg:py-3 inline-block max-w-full">
                            <p className="text-sm lg:text-base break-words">{message.content}</p>
                          </div>
                          <div className="text-caption mt-1">{new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' })}</div>
                        </div>
                      </div>
                    ) : (
                      <div className="flex items-start gap-3 lg:gap-4">
                        <div className="w-7 h-7 lg:w-8 lg:h-8 rounded-full bg-[var(--color-accent)] flex items-center justify-center flex-shrink-0">
                          <svg className="w-4 h-4 lg:w-5 lg:h-5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                          </svg>
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="mb-2">
                            <span className="font-medium text-sm lg:text-base">Answer</span>
                          </div>
                          <div className="prose prose-invert max-w-none">
                            {(() => {
                              const extracted = extractKeyIdea(message.content);
                              if (extracted) {
                                return (
                                  <>
                                    <div className="text-sm lg:text-base mb-4 break-words whitespace-pre-line leading-relaxed">
                                      {extracted.rest}
                                    </div>
                                    <div className="key-idea mb-4">
                                      <div className="text-xs lg:text-sm font-medium text-[var(--color-accent)] mb-2 tracking-wide uppercase">
                                        Key Idea
                                      </div>
                                      <div className="text-sm lg:text-base break-words leading-relaxed">{extracted.keyIdea}</div>
                                    </div>
                                  </>
                                );
                              }
                              return (
                                <div className="text-sm lg:text-base whitespace-pre-line break-words leading-relaxed">
                                  {message.content}
                                </div>
                              );
                            })()}
                          </div>

                          {message.sources && message.sources.length > 0 && (
                            <div className="mt-4 p-3 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg">
                              <div className="flex items-center gap-2 mb-2">
                                <svg className="w-4 h-4 text-[var(--color-text-secondary)] flex-shrink-0" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                                </svg>
                                <span className="text-xs lg:text-sm font-medium">NCERT Source</span>
                              </div>
                              <div className="text-xs lg:text-sm text-[var(--color-text-tertiary)] break-words">{message.sources[0]}</div>
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                ))}
                {isLoading && (
                  <div className="flex items-start gap-3 lg:gap-4">
                    <div className="w-7 h-7 lg:w-8 lg:h-8 rounded-full bg-[var(--color-accent)] flex items-center justify-center flex-shrink-0">
                      <svg className="w-4 h-4 lg:w-5 lg:h-5 text-white animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
                      </svg>
                    </div>
                    <div className="text-sm lg:text-base text-[var(--color-text-secondary)]">Searching NCERT knowledge base...</div>
                  </div>
                )}
                <div ref={messagesEndRef} />
              </div>
            )}
          </div>
        </div>

        {/* Input - Only show in chapter view */}
        {viewMode === 'chapter' && (
          <div className="border-t border-[var(--color-border)] bg-[var(--color-background)] flex-shrink-0">
            <form onSubmit={handleSubmit} className="max-w-3xl mx-auto px-4 lg:px-6 py-3 lg:py-4">
              <div className="flex items-end gap-2 lg:gap-3">
                <div className="flex-1 min-w-0">
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
                    className="w-full px-3 lg:px-4 py-2 lg:py-3 bg-[var(--color-surface)] border border-[var(--color-border)] rounded-lg text-sm lg:text-base resize-none focus:outline-none focus:border-[var(--color-accent)] transition-colors"
                    style={{ minHeight: '44px', maxHeight: '120px' }}
                  />
                  {currentChapter && (
                    <div className="flex items-center gap-2 mt-1.5 text-xs lg:text-sm text-[var(--color-text-tertiary)]">
                      <span>{currentSubjectData?.name}</span>
                      <span>·</span>
                      <span>Ch {currentChapter.number}</span>
                    </div>
                  )}
                </div>
                <button
                  type="submit"
                  disabled={!input.trim() || isLoading}
                  className="w-11 h-11 lg:w-12 lg:h-12 bg-[var(--color-accent)] hover:bg-[var(--color-accent-hover)] disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg flex items-center justify-center transition-colors flex-shrink-0"
                >
                  <svg className="w-4 h-4 lg:w-5 lg:h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
                  </svg>
                </button>
              </div>
            </form>
          </div>
        )}
      </main>
    </div>
  );
}
