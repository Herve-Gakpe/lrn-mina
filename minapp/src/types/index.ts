export interface VocabularyItem {
  text_fr: string;
  text_mina: string;
  note: string;
}

export type QuizDirection = 'fr_to_mina' | 'mina_to_fr';

export interface Question {
  question: string;
  correctAnswer: string;
  options: string[];
  direction: QuizDirection;
} 