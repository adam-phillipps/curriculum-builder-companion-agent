'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import { buildApiUrl } from '../config/api';
import InteractivePathwayGraph from './InteractivePathwayGraph';

// Learning Goal Section Component
function LearningGoalSection({ userId, profile, onGoalSet }: { userId: number, profile: any, onGoalSet: () => void }) {
  const [showGoalSetter, setShowGoalSetter] = useState(false);
  const [learningGoal, setLearningGoal] = useState('');
  const [goalSuggestions, setGoalSuggestions] = useState<any[]>([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedGoal, setSelectedGoal] = useState<any>(null);
  const [searchingGoals, setSearchingGoals] = useState(false);
  const [saving, setSaving] = useState(false);

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

  const handleSaveGoal = async () => {
    if (!selectedGoal) return;
    
    setSaving(true);
    try {
      let goalId = selectedGoal.outcome_id;
      
      // If it's a custom goal, create it first
      if (!selectedGoal.is_existing) {
        const goalResponse = await fetch(buildApiUrl('learning-outcomes/'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            name: selectedGoal.name,
            description: selectedGoal.description,
            domain: selectedGoal.domain,
            difficulty_level: selectedGoal.difficulty_level,
            tags: selectedGoal.tags,
            created_by_user_id: userId
          })
        });
        
        if (goalResponse.ok) {
          const newGoal = await goalResponse.json();
          goalId = newGoal.id;
        }
      }
      
      // Set as primary goal
      if (goalId) {
        await fetch(buildApiUrl(`users/${userId}/primary-goal`), {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ learning_outcome_id: goalId })
        });
        
        // Reset form and refresh profile
        setShowGoalSetter(false);
        setLearningGoal('');
        setSelectedGoal(null);
        onGoalSet();
      }
    } catch (error) {
      console.error('Failed to set learning goal:', error);
      alert('Failed to set learning goal. Please try again.');
    } finally {
      setSaving(false);
    }
  };

  if (!profile.current_pathway_id && !showGoalSetter) {
    return (
      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mb-6">
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <div className="text-yellow-600 mr-3">⚠️</div>
            <div>
              <h3 className="text-sm font-medium text-yellow-800">Set Your Learning Goal</h3>
              <p className="text-sm text-yellow-700 mt-1">
                To see your complete learning pathway, set a specific learning outcome goal.
              </p>
            </div>
          </div>
          <button
            onClick={() => setShowGoalSetter(true)}
            className="bg-yellow-600 text-white px-4 py-2 rounded text-sm hover:bg-yellow-700"
          >
            Set Goal
          </button>
        </div>
      </div>
    );
  }

  if (showGoalSetter) {
    return (
      <div className="bg-white border rounded-lg p-6 mb-6">
        <h3 className="text-lg font-semibold mb-4">Set Your Learning Goal</h3>
        
        <div className="relative">
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
        
        <div className="flex space-x-3 mt-4">
          <button
            onClick={() => setShowGoalSetter(false)}
            className="bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
          >
            Cancel
          </button>
          <button
            onClick={handleSaveGoal}
            disabled={!selectedGoal || saving}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {saving ? 'Saving...' : 'Save Goal'}
          </button>
        </div>
      </div>
    );
  }

  return null;
}

interface LearnerProfile {
  id: number;
  user_id: number;
  learning_goals?: Array<{ goal: string; priority: string }>;
  target_outcomes?: Array<{ outcome: string; deadline: string }>;
  total_content_completed: number;
  total_learning_hours: number;
}

interface ContentProgress {
  content_id: number;
  status: string;
  progress_percentage: number;
  time_spent_minutes: number;
}

interface LearnerProfileProps {
  userId: number;
}

export default function LearnerProfile({ userId }: LearnerProfileProps) {
  const [profile, setProfile] = useState<LearnerProfile | null>(null);
  const [progress, setProgress] = useState<ContentProgress[]>([]);
  const [loading, setLoading] = useState(true);


  useEffect(() => {
    loadProfileData();
  }, [userId]);

  const loadProfileData = async () => {
    setLoading(true);
    try {
      const [profileResponse, progressResponse] = await Promise.all([
        api.get(`/users/${userId}/learner-profile`),
        api.get(`/users/${userId}/content-progress`)
      ]);
      setProfile(profileResponse.data);
      setProgress(progressResponse.data);
    } catch (error) {
      console.error('Failed to load profile:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return <div className="p-6">Loading profile...</div>;
  }

  if (!profile) {
    return <div className="p-6">Profile not found</div>;
  }

  const completedContent = progress.filter(p => p.status === 'completed').length;
  const inProgressContent = progress.filter(p => p.status === 'in_progress').length;
  const totalProgress = progress.reduce((sum, p) => sum + p.progress_percentage, 0) / progress.length || 0;

  return (
    <div className="p-6 space-y-6">
      <div className="border-b pb-4">
        <h1 className="text-2xl font-bold">Learner Profile</h1>
        <p className="text-gray-600">Track your learning journey and progress</p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">{profile.total_content_completed}</div>
          <div className="text-sm text-gray-600">Content Completed</div>
        </div>
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-green-600">{profile.total_learning_hours}</div>
          <div className="text-sm text-gray-600">Learning Hours</div>
        </div>
        <div className="bg-purple-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-purple-600">{completedContent}</div>
          <div className="text-sm text-gray-600">Completed Items</div>
        </div>
        <div className="bg-orange-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-orange-600">{inProgressContent}</div>
          <div className="text-sm text-gray-600">In Progress</div>
        </div>
      </div>

      {/* Progress Visualization */}
      <div className="bg-white border rounded-lg p-6">
        <h2 className="text-lg font-semibold mb-4">Learning Progress</h2>
        <div className="space-y-3">
          <div className="flex justify-between text-sm">
            <span>Overall Progress</span>
            <span>{Math.round(totalProgress)}%</span>
          </div>
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${totalProgress}%` }}
            />
          </div>
        </div>
      </div>

      {/* Learning Goals */}
      {profile.learning_goals && profile.learning_goals.length > 0 && (
        <div className="bg-white border rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Learning Goals</h2>
          <div className="space-y-2">
            {profile.learning_goals.map((goal, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                <span>{goal.goal}</span>
                <span className={`px-2 py-1 rounded text-xs ${
                  goal.priority === 'high' ? 'bg-red-100 text-red-800' :
                  goal.priority === 'medium' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  {goal.priority}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Target Outcomes */}
      {profile.target_outcomes && profile.target_outcomes.length > 0 && (
        <div className="bg-white border rounded-lg p-6">
          <h2 className="text-lg font-semibold mb-4">Target Outcomes</h2>
          <div className="space-y-2">
            {profile.target_outcomes.map((outcome, index) => (
              <div key={index} className="p-3 bg-gray-50 rounded">
                <div className="font-medium">{outcome.outcome}</div>
                <div className="text-sm text-gray-600">Deadline: {outcome.deadline}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Learning Goal Setting */}
      <LearningGoalSection userId={userId} profile={profile} onGoalSet={loadProfileData} />

      {/* Interactive Pathway Graph with Chain Rule */}
      <InteractivePathwayGraph 
        userId={userId} 
        pathwayId={profile.current_pathway_id || 0}
      />
    </div>
  );
}