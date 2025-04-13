import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

interface ResultsState {
  score: number;
  total: number;
}

const Results: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { score, total } = location.state as ResultsState;
  const percentage = Math.round((score / total) * 100);

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-center mb-8">Résultats</h1>
      <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
        <p className="text-2xl text-center mb-4">
          Vous avez obtenu {score} bonnes réponses sur {total}
        </p>
        <div className="w-full bg-gray-200 rounded-full h-4 mb-4">
          <div
            className="bg-blue-500 h-4 rounded-full"
            style={{ width: `${percentage}%` }}
          ></div>
        </div>
        <p className="text-center text-xl font-semibold">{percentage}%</p>
      </div>
      <div className="flex flex-col gap-4">
        <button
          onClick={() => navigate('/')}
          className="bg-blue-500 text-white py-3 px-6 rounded-lg text-lg font-semibold hover:bg-blue-600 transition-colors"
        >
          Retour aux thèmes
        </button>
        <button
          onClick={() => navigate(-1)}
          className="bg-gray-500 text-white py-3 px-6 rounded-lg text-lg font-semibold hover:bg-gray-600 transition-colors"
        >
          Réessayer
        </button>
      </div>
    </div>
  );
};

export default Results; 