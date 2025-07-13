'use client';

import { useState, useEffect } from 'react';
import { buildApiUrl } from '../config/api';

interface LearningGoalSelectorProps {
  onGoalSelected: (goal: any) => void;
  initialGoal?: string;
  className?: string;
}

export default function LearningGoalSelector({ onGoalSelected, initialGoal = '', className = '' }: LearningGoalSelectorProps) {
  const [learningGoal, setLearningGoal] = useState(initialGoal);
  const [goalSuggestions, setGoalSuggestions] = useState<any[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedGoal, setSelectedGoal] = useState<any>(null);
  const [searchingGoals, setSearchingGoals] = useState(false);

  // Debounced search for learning goals
  useEffect(() => {
    if (!learningGoal.trim() || learningGoal.length < 3) {
      setGoalSuggestions([]);
      setShowSuggestions(false);
      return;
    }
    
    const timeoutId = setTimeout(async () => {
      await searchLearningGoals(learningGoal);
    }, 800);
    
    return () => clearTimeout(timeoutId);
  }, [learningGoal]);
  
  const searchLearningGoals = async (query: string) => {
    setSearchingGoals(true);
    try {
      const response = await fetch(
        buildApiUrl(`learning-outcomes/search?query=${encodeURIComponent(query)}&max_results=5`)
      );
      
      if (response.ok) {
        const suggestions = await response.json();
        setGoalSuggestions(suggestions);
        setShowSuggestions(true);
      } else {
        // Fallback: show custom option
        setGoalSuggestions([{
          outcome_id: null,
          name: query,
          description: `Custom learning goal: ${query}`,
          domain: "custom",
          difficulty_level: "intermediate",
          tags: [],
          similarity_score: 0.0,
          is_existing: false
        }]);
        setShowSuggestions(true);
      }
    } catch (error) {
      // Fallback: show custom option
      setGoalSuggestions([{
        outcome_id: null,
        name: query,
        description: `Custom learning goal: ${query}`,
        domain: "custom",
        difficulty_level: "intermediate",
        tags: [],
        similarity_score: 0.0,
        is_existing: false
      }]);
      setShowSuggestions(true);
    } finally {
      setSearchingGoals(false);
    }
  };
  
  const handleGoalSelect = (suggestion: any) => {
    setSelectedGoal(suggestion);
    setLearningGoal(suggestion.name);
    setShowSuggestions(false);
    onGoalSelected(suggestion);
  };

  return (
    <div className={`relative ${className}`}>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        Learning Goal
      </label>
      <input
        type="text"
        value={learningGoal}
        onChange={(e) => setLearningGoal(e.target.value)}
        placeholder="e.g., 'Python programming', 'AWS architecture', 'Machine learning'..."
        className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
      />
      <p className="text-xs text-gray-500 mt-1">
        We'll suggest similar goals or you can create your own
      </p>
      
      {/* Goal Suggestions Dropdown */}
      {showSuggestions && goalSuggestions.length > 0 && (
        <div className="absolute z-10 w-full mt-1 bg-white border border-gray-300 rounded-md shadow-lg max-h-60 overflow-y-auto">
          {goalSuggestions
            .sort((a, b) => {
              if (a.is_existing && !b.is_existing) return -1;
              if (!a.is_existing && b.is_existing) return 1;
              if (a.is_existing && b.is_existing) return b.similarity_score - a.similarity_score;
              return 0;
            })
            .map((suggestion, index) => (
            <div
              key={`${suggestion.outcome_id || 'custom'}-${index}`}
              onClick={() => handleGoalSelect(suggestion)}
              className="px-3 py-2 hover:bg-gray-100 cursor-pointer border-b border-gray-100 last:border-b-0"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="font-medium text-sm">{suggestion.name}</div>
                  <div className="text-xs text-gray-600 truncate">{suggestion.description}</div>
                  <div className="flex items-center space-x-2 mt-1">
                    <span className="text-xs bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
                      {suggestion.domain.replace('_', ' ')}
                    </span>
                    <span className="text-xs bg-gray-100 text-gray-700 px-2 py-0.5 rounded">
                      {suggestion.difficulty_level}
                    </span>
                  </div>
                </div>
                <div className="ml-2 text-right">
                  {suggestion.is_existing ? (
                    <div className="text-xs text-green-600">
                      {Math.round(suggestion.similarity_score * 100)}% match
                    </div>
                  ) : (
                    <div className="text-xs text-blue-600">Create new</div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      
      {searchingGoals && (
        <div className="text-xs text-blue-600 mt-1">🔄 Searching for similar goals...</div>
      )}
      
      {selectedGoal && (
        <div className="mt-2 p-2 bg-green-50 border border-green-200 rounded text-sm">
          <div className="font-medium text-green-800">Selected: {selectedGoal.name}</div>
          <div className="text-green-600 text-xs">
            {selectedGoal.is_existing ? 'Existing goal' : 'Will create new goal'}
          </div>
        </div>
      )}
    </div>
  );
}