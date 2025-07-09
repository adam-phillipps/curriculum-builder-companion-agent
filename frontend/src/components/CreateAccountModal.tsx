'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';

interface CreateAccountModalProps {
  isOpen: boolean;
  onClose: () => void;
  onAccountCreated: (user: any) => void;
}

export default function CreateAccountModal({ isOpen, onClose, onAccountCreated }: CreateAccountModalProps) {
  const [availableRoles, setAvailableRoles] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    first_name: '',
    last_name: '',
    email: '',
    current_role: 'learner'
  });
  
  // Learning goal states
  const [learningGoal, setLearningGoal] = useState('');
  const [goalSuggestions, setGoalSuggestions] = useState<any[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedGoal, setSelectedGoal] = useState<any>(null);
  const [searchingGoals, setSearchingGoals] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadRoles();
    }
  }, [isOpen]);

  const loadRoles = async () => {
    try {
      const response = await api.get('/users/roles/available');
      setAvailableRoles(response.data);
    } catch (error) {
      console.error('Failed to load roles:', error);
      // Fallback roles if API fails
      setAvailableRoles(['learner', 'builder', 'curriculum_architect', 'developer']);
    }
  };

  // Debounced search for learning goals
  useEffect(() => {
    if (!learningGoal.trim() || learningGoal.length < 3) {
      setGoalSuggestions([]);
      setShowSuggestions(false);
      return;
    }
    
    const timeoutId = setTimeout(async () => {
      await searchLearningGoals(learningGoal);
    }, 800); // Increased debounce to reduce API calls
    
    return () => clearTimeout(timeoutId);
  }, [learningGoal]);
  
  const searchLearningGoals = async (query: string) => {
    setSearchingGoals(true);
    try {
      const response = await fetch(
        `http://localhost:8001/api/v1/learning-outcomes/search?query=${encodeURIComponent(query)}&max_results=5`
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
  };
  
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    
    try {
      console.log('Creating account with data:', formData);
      const response = await api.post('/users/', formData);
      const user = response.data;
      console.log('Account created:', user);
      
      // If user selected a learning goal, set it as their primary goal
      if (selectedGoal && user.id) {
        try {
          let goalId = selectedGoal.outcome_id;
          
          // If it's a custom goal, create it first
          if (!selectedGoal.is_existing) {
            const goalResponse = await fetch('http://localhost:8001/api/v1/learning-outcomes/', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({
                name: selectedGoal.name,
                description: selectedGoal.description,
                domain: selectedGoal.domain,
                difficulty_level: selectedGoal.difficulty_level,
                tags: selectedGoal.tags,
                created_by_user_id: user.id
              })
            });
            
            if (goalResponse.ok) {
              const newGoal = await goalResponse.json();
              goalId = newGoal.id;
            }
          }
          
          // Set as primary goal
          if (goalId) {
            await fetch(`http://localhost:8001/users/${user.id}/primary-goal`, {
              method: 'PUT',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ learning_outcome_id: goalId })
            });
          }
        } catch (goalError) {
          console.error('Failed to set learning goal:', goalError);
          // Don't fail account creation if goal setting fails
        }
      }
      
      onAccountCreated(user);
      onClose();
      setFormData({ first_name: '', last_name: '', email: '', current_role: 'learner' });
      setLearningGoal('');
      setSelectedGoal(null);
    } catch (error) {
      console.error('Failed to create account:', error);
      alert('Failed to create account: ' + (error instanceof Error ? error.message : 'Unknown error'));
    } finally {
      setLoading(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Create Account</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              First Name *
            </label>
            <input
              type="text"
              required
              value={formData.first_name}
              onChange={(e) => setFormData({...formData, first_name: e.target.value})}
              className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Last Name
            </label>
            <input
              type="text"
              value={formData.last_name}
              onChange={(e) => setFormData({...formData, last_name: e.target.value})}
              className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Email
            </label>
            <input
              type="email"
              value={formData.email}
              onChange={(e) => setFormData({...formData, email: e.target.value})}
              className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Your Role *
            </label>
            <select
              required
              value={formData.current_role}
              onChange={(e) => setFormData({...formData, current_role: e.target.value})}
              className="w-full p-2 border rounded focus:ring-2 focus:ring-blue-500"
            >
              {availableRoles.length === 0 ? (
                <option value="learner">Loading roles...</option>
              ) : (
                availableRoles.map((role) => (
                  <option key={role} value={role}>
                    {role.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                  </option>
                ))
              )}
            </select>
            {availableRoles.length > 0 && (
              <p className="text-xs text-gray-500 mt-1">
                {availableRoles.length} roles available
              </p>
            )}
          </div>

          {/* Learning Goal Field - Only show for learners */}
          {formData.current_role === 'learner' && (
            <div className="relative">
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Learning Goal (Optional)
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
                      // Sort existing outcomes by similarity score (highest first), then custom option last
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
                    {selectedGoal.is_existing ? 'Existing goal' : 'Will create new goal (pending approval)'}
                  </div>
                </div>
              )}
            </div>
          )}
        </form>
        
        {/* Submit buttons - Always visible outside form */}
        <div className="flex space-x-3 mt-6">
          <button
            type="button"
            onClick={onClose}
            className="flex-1 bg-gray-300 text-gray-700 py-2 px-4 rounded hover:bg-gray-400"
          >
            Cancel
          </button>
          <button
            onClick={handleSubmit}
            disabled={loading}
            className="flex-1 bg-blue-600 text-white py-2 px-4 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Creating...' : 'Create Account'}
          </button>
        </div>
      </div>
    </div>
  );
}