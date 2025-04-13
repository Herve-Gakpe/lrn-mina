import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import vocabData from '../data/vocab_mina.json';
import { VocabularyItem, Question, QuizDirection } from '../types';

const ThemeQuiz: React.FC = () => {
  const { theme } = useParams<{ theme: string }>();
  const navigate = useNavigate();
  const [currentQuestion, setCurrentQuestion] = useState<number>(0);
  const [score, setScore] = useState<number>(0);
  const [questions, setQuestions] = useState<Question[]>([]);
  const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
  const [showFeedback, setShowFeedback] = useState<boolean>(false);

  useEffect(() => {
    // Filter vocabulary by theme
    const themeVocab = (vocabData as VocabularyItem[]).filter(item => item.note === theme);
    
    // Generate questions
    const generatedQuestions = themeVocab.map(item => {
      const direction: QuizDirection = Math.random() > 0.5 ? 'fr_to_mina' : 'mina_to_fr';
      const question = direction === 'fr_to_mina' ? item.text_fr : item.text_mina;
      const correctAnswer = direction === 'fr_to_mina' ? item.text_mina : item.text_fr;
      
      // Generate options
      const otherItems = themeVocab.filter(i => i !== item);
      const options = [correctAnswer];
      while (options.length < 4) {
        const randomItem = otherItems[Math.floor(Math.random() * otherItems.length)];
        const option = direction === 'fr_to_mina' ? randomItem.text_mina : randomItem.text_fr;
        if (!options.includes(option)) {
          options.push(option);
        }
      }
      
      // Shuffle options
      return {
        question,
        correctAnswer,
        options: options.sort(() => Math.random() - 0.5),
        direction
      };
    });

    setQuestions(generatedQuestions.sort(() => Math.random() - 0.5));
  }, [theme]);

  const handleAnswer = (answer: string) => {
    setSelectedAnswer(answer);
    setShowFeedback(true);
    
    if (answer === questions[currentQuestion].correctAnswer) {
      setScore(score + 1);
    }

    setTimeout(() => {
      if (currentQuestion < questions.length - 1) {
        setCurrentQuestion(currentQuestion + 1);
        setSelectedAnswer(null);
        setShowFeedback(false);
      } else {
        navigate('/results', { state: { score, total: questions.length } });
      }
    }, 1500);
  };

  if (questions.length === 0) {
    return <div className="container mx-auto px-4 py-8">Chargement...</div>;
  }

  const current = questions[currentQuestion];

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h2 className="text-2xl font-bold mb-4">Question {currentQuestion + 1}/{questions.length}</h2>
        <p className="text-xl mb-6">{current.question}</p>
        <div className="grid gap-4">
          {current.options.map((option) => (
            <button
              key={option}
              onClick={() => handleAnswer(option)}
              disabled={showFeedback}
              className={`py-3 px-6 rounded-lg text-lg font-semibold transition-colors ${
                showFeedback
                  ? option === current.correctAnswer
                    ? 'bg-green-500 text-white'
                    : option === selectedAnswer
                    ? 'bg-red-500 text-white'
                    : 'bg-gray-200 text-gray-700'
                  : 'bg-blue-500 text-white hover:bg-blue-600'
              }`}
            >
              {option}
            </button>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ThemeQuiz; 