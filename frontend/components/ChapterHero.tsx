import Image from 'next/image';

interface ChapterHeroProps {
  subject: 'science' | 'mathematics';
  chapterNumber: number;
  title: string;
  description: string;
  heroImage?: string;
  compact?: boolean;
}

export function ChapterHero({
  subject,
  chapterNumber,
  title,
  description,
  heroImage,
  compact = false,
}: ChapterHeroProps) {
  return (
    <div className={`chapter-hero ${compact ? 'compact' : ''}`}>
      {/* Hero artwork background with integrated blending */}
      {heroImage && (
        <div className="chapter-hero-image-container">
          <Image
            src={heroImage}
            alt=""
            fill
            className="chapter-hero-image"
            priority
            quality={90}
          />
        </div>
      )}

      {/* Content wrapper */}
      <div className="chapter-hero-content">
        {/* Main chapter information */}
        <div className="chapter-hero-main">
          <div className="text-label text-[var(--color-text-secondary)]">
            CHAPTER {chapterNumber}
          </div>
          <h1 className="text-chapter-display text-[var(--color-text-primary)]">
            {title}
          </h1>
          {!compact && (
            <p className="text-[15px] text-[var(--color-text-secondary)] leading-relaxed">
              {description}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
