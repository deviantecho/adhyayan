/**
 * NCERT Class 10 Curriculum Data
 *
 * This maps to the actual data available in the RAG system.
 */

export interface Chapter {
  id: string;
  number: number;
  title: string;
  description: string;
  suggestedQuestions: string[];
}

export interface Subject {
  id: 'science' | 'mathematics';
  name: string;
  description: string;
  chapters: Chapter[];
}

export const SCIENCE_CHAPTERS: Chapter[] = [
  {
    id: 'chapter1',
    number: 1,
    title: 'Chemical Reactions and Equations',
    description: 'Understand how substances change and why it matters.',
    suggestedQuestions: [
      'Why do we need to balance a chemical equation?',
      'What happens during a chemical reaction?',
      'What is the law of conservation of mass?',
    ],
  },
  {
    id: 'chapter2',
    number: 2,
    title: 'Acids, Bases and Salts',
    description: 'Explore the properties and reactions of acids and bases.',
    suggestedQuestions: [
      'What are the properties of acids and bases?',
      'How do indicators help identify acids and bases?',
      'What is the pH scale?',
    ],
  },
  {
    id: 'chapter3',
    number: 3,
    title: 'Metals and Non-metals',
    description: 'Learn about the physical and chemical properties of metals.',
    suggestedQuestions: [
      'What are the properties of metals?',
      'How do metals react with acids?',
      'What is corrosion?',
    ],
  },
  {
    id: 'chapter4',
    number: 4,
    title: 'Carbon and its Compounds',
    description: 'Discover the unique bonding nature of carbon.',
    suggestedQuestions: [
      'Why does carbon form covalent bonds?',
      'What are hydrocarbons?',
      'What is the structure of carbon compounds?',
    ],
  },
  {
    id: 'chapter5',
    number: 5,
    title: 'Periodic Classification of Elements',
    description: 'Understand the organization of elements in the periodic table.',
    suggestedQuestions: [
      'How are elements arranged in the periodic table?',
      'What are periods and groups?',
      'What trends exist in the periodic table?',
    ],
  },
  {
    id: 'chapter6',
    number: 6,
    title: 'Life Processes',
    description: 'Study the essential functions that maintain life.',
    suggestedQuestions: [
      'What are life processes?',
      'How does nutrition occur in living organisms?',
      'What is respiration?',
    ],
  },
  {
    id: 'chapter7',
    number: 7,
    title: 'Control and Coordination',
    description: 'Learn how organisms respond to their environment.',
    suggestedQuestions: [
      'How does the nervous system work?',
      'What is the role of hormones?',
      'How do plants respond to stimuli?',
    ],
  },
  {
    id: 'chapter8',
    number: 8,
    title: 'How do Organisms Reproduce?',
    description: 'Explore reproduction in plants and animals.',
    suggestedQuestions: [
      'What is reproduction?',
      'What is the difference between asexual and sexual reproduction?',
      'How does reproduction occur in plants?',
    ],
  },
  {
    id: 'chapter9',
    number: 9,
    title: 'Heredity and Evolution',
    description: 'Understand how traits are inherited and species evolve.',
    suggestedQuestions: [
      'What is heredity?',
      'How do traits get inherited?',
      'What is evolution?',
    ],
  },
  {
    id: 'chapter10',
    number: 10,
    title: 'Light – Reflection and Refraction',
    description: 'Study the behavior of light and its properties.',
    suggestedQuestions: [
      'What is reflection of light?',
      'What is refraction?',
      'How do mirrors and lenses work?',
    ],
  },
  {
    id: 'chapter11',
    number: 11,
    title: 'Human Eye and Colourful World',
    description: 'Explore the structure and function of the human eye.',
    suggestedQuestions: [
      'How does the human eye work?',
      'What are defects of vision?',
      'How does a prism disperse light?',
    ],
  },
  {
    id: 'chapter12',
    number: 12,
    title: 'Electricity',
    description: 'Learn about electric current, circuits, and power.',
    suggestedQuestions: [
      'What is electric current?',
      "What is Ohm's law?",
      'How is electrical energy calculated?',
    ],
  },
  {
    id: 'chapter13',
    number: 13,
    title: 'Magnetic Effects of Electric Current',
    description: 'Discover the relationship between electricity and magnetism.',
    suggestedQuestions: [
      'What is a magnetic field?',
      'How does an electric motor work?',
      'What is electromagnetic induction?',
    ],
  },
];

export const MATHEMATICS_CHAPTERS: Chapter[] = [
  {
    id: 'chapter1',
    number: 1,
    title: 'Real Numbers',
    description: 'Study the properties and operations on real numbers.',
    suggestedQuestions: [
      "What is Euclid's division algorithm?",
      'How do you find the HCF of two numbers?',
      'What is the Fundamental Theorem of Arithmetic?',
    ],
  },
  {
    id: 'chapter2',
    number: 2,
    title: 'Polynomials',
    description: 'Learn about algebraic expressions and their properties.',
    suggestedQuestions: [
      'What is a polynomial?',
      'How do you find zeros of a polynomial?',
      'What is the relationship between zeros and coefficients?',
    ],
  },
  {
    id: 'chapter3',
    number: 3,
    title: 'Pair of Linear Equations in Two Variables',
    description: 'Solve systems of linear equations using various methods.',
    suggestedQuestions: [
      'What is a linear equation in two variables?',
      'How do you solve simultaneous equations?',
      'What are the graphical and algebraic methods?',
    ],
  },
  {
    id: 'chapter4',
    number: 4,
    title: 'Quadratic Equations',
    description: 'Explore equations of degree two and their solutions.',
    suggestedQuestions: [
      'What is a quadratic equation?',
      'How do you solve quadratic equations by factorization?',
      'What is the quadratic formula?',
    ],
  },
  {
    id: 'chapter5',
    number: 5,
    title: 'Arithmetic Progressions',
    description: 'Study sequences with constant differences.',
    suggestedQuestions: [
      'What is an arithmetic progression?',
      'How do you find the nth term?',
      'How do you calculate the sum of an AP?',
    ],
  },
  {
    id: 'chapter6',
    number: 6,
    title: 'Triangles',
    description: 'Learn about similarity and congruence of triangles.',
    suggestedQuestions: [
      'What are similar triangles?',
      'What is the Pythagoras theorem?',
      'What are the criteria for similarity?',
    ],
  },
  {
    id: 'chapter7',
    number: 7,
    title: 'Coordinate Geometry',
    description: 'Locate points and analyze geometric figures on a plane.',
    suggestedQuestions: [
      'How do you find the distance between two points?',
      'What is the section formula?',
      'How do you find the area of a triangle?',
    ],
  },
  {
    id: 'chapter8',
    number: 8,
    title: 'Introduction to Trigonometry',
    description: 'Explore relationships between angles and sides of triangles.',
    suggestedQuestions: [
      'What are trigonometric ratios?',
      'How do you find sin, cos, and tan values?',
      'What are trigonometric identities?',
    ],
  },
  {
    id: 'chapter9',
    number: 9,
    title: 'Some Applications of Trigonometry',
    description: 'Apply trigonometry to solve real-world problems.',
    suggestedQuestions: [
      'How do you calculate heights and distances?',
      'What is the angle of elevation?',
      'What is the angle of depression?',
    ],
  },
  {
    id: 'chapter10',
    number: 10,
    title: 'Circles',
    description: 'Study properties of circles, tangents, and secants.',
    suggestedQuestions: [
      'What is a tangent to a circle?',
      'How many tangents can be drawn from a point?',
      'What are the properties of tangents?',
    ],
  },
  {
    id: 'chapter11',
    number: 11,
    title: 'Areas Related to Circles',
    description: 'Calculate areas of sectors, segments, and combinations.',
    suggestedQuestions: [
      'How do you find the area of a sector?',
      'What is the area of a segment?',
      'How do you solve problems with combined shapes?',
    ],
  },
  {
    id: 'chapter12',
    number: 12,
    title: 'Surface Areas and Volumes',
    description: 'Calculate measurements of three-dimensional objects.',
    suggestedQuestions: [
      'How do you find surface area of combined solids?',
      'How do you calculate volume of combined shapes?',
      'What happens when one shape is converted to another?',
    ],
  },
  {
    id: 'chapter13',
    number: 13,
    title: 'Statistics',
    description: 'Analyze and interpret data using statistical methods.',
    suggestedQuestions: [
      'What is the mean of grouped data?',
      'How do you find the median?',
      'What is the mode of a distribution?',
    ],
  },
  {
    id: 'chapter14',
    number: 14,
    title: 'Probability',
    description: 'Study the likelihood of events and outcomes.',
    suggestedQuestions: [
      'What is probability?',
      'How do you calculate probability of an event?',
      'What is the probability of complementary events?',
    ],
  },
];

export const SUBJECTS: Subject[] = [
  {
    id: 'science',
    name: 'Science',
    description: 'Explore the natural world through physics, chemistry, and biology.',
    chapters: SCIENCE_CHAPTERS,
  },
  {
    id: 'mathematics',
    name: 'Mathematics',
    description: 'Develop logical thinking and problem-solving skills.',
    chapters: MATHEMATICS_CHAPTERS,
  },
];

export function getSubject(subjectId: 'science' | 'mathematics'): Subject | undefined {
  return SUBJECTS.find(s => s.id === subjectId);
}

export function getChapter(subjectId: 'science' | 'mathematics', chapterId: string): Chapter | undefined {
  const subject = getSubject(subjectId);
  return subject?.chapters.find(c => c.id === chapterId);
}
