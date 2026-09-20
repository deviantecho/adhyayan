/**
 * Load hero assets and quote data
 */

interface QuoteData {
  text: string;
  attribution: string;
  labels: string[];
}

const HERO_ASSETS = {
  science: {
    image: '/hero/science-hero.png',
    quote: {
      text: 'In every reaction, matter is conserved.',
      attribution: 'NCERT Class 10',
      labels: ['OBSERVE', 'THINK', 'LEARN', 'APPLY'],
    } as QuoteData,
  },
  mathematics: {
    image: '/hero/mathematics-hero.png',
    quote: {
      text: 'Patterns become clearer when we learn to see them.',
      attribution: 'Editorial statement',
      labels: ['EXPLORE', 'REASON', 'SOLVE', 'CREATE'],
    } as QuoteData,
  },
};

export function getHeroAssets(subject: 'science' | 'mathematics') {
  return HERO_ASSETS[subject];
}
