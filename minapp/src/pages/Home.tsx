import React from 'react';
import { useNavigate } from 'react-router-dom';
import vocabData from '../data/vocab_mina.json';
import { VocabularyItem } from '../types';

const Home: React.FC = () => {
  const navigate = useNavigate();
  
  // Get unique themes from the vocabulary data
  const themes = Array.from(new Set((vocabData as VocabularyItem[]).map(item => item.note)));

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-center mb-8">Apprendre le Mina</h1>
      <div className="grid gap-4">
        {themes.map((theme) => (
          <button
            key={theme}
            onClick={() => navigate(`/theme/${theme}`)}
            className="bg-blue-500 text-white py-4 px-6 rounded-lg text-lg font-semibold hover:bg-blue-600 transition-colors"
          >
            {theme}
          </button>
        ))}
      </div>
    </div>
  );
};

export default Home; 