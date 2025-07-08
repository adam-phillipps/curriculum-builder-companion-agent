'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';
import InteractivePathwayGraph from './InteractivePathwayGraph';

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

      {/* Interactive Pathway Graph with Chain Rule */}
      {profile.current_pathway_id && (
        <InteractivePathwayGraph 
          userId={userId} 
          pathwayId={profile.current_pathway_id}
        />
      )}
    </div>
  );
}