'use client';

import { useState } from 'react';
import ContentDashboard from '@/components/ContentDashboard';
import LearnerProfile from '@/components/LearnerProfile';
import UserSignInModal from '@/components/UserSignInModal';

interface User {
  id: number;
  first_name?: string;
  last_name?: string;
  current_role: string;
}

export default function HomePage() {
  const [currentUser, setCurrentUser] = useState<User | null>(null);
  const [activeTab, setActiveTab] = useState<string>('dashboard');
  const [showSignInModal, setShowSignInModal] = useState(false);

  const handleSignIn = (user: User) => {
    setCurrentUser(user);
    // Set default tab based on role
    if (user.current_role === 'learner') {
      setActiveTab('profile');
    } else {
      setActiveTab('dashboard');
    }
  };

  const handleSignOut = () => {
    setCurrentUser(null);
    setActiveTab('dashboard');
  };

  const getRoleBasedTabs = () => {
    if (!currentUser) return [{ id: 'dashboard', label: 'Content Dashboard' }];
    
    const baseTabs = [{ id: 'dashboard', label: 'Content Dashboard' }];
    
    if (currentUser.current_role === 'learner') {
      baseTabs.unshift({ id: 'profile', label: 'My Learning Profile' });
    }
    
    if (currentUser.current_role === 'builder' || currentUser.current_role === 'curriculum_architect') {
      baseTabs.push({ id: 'builder', label: 'Content Builder' });
    }
    
    return baseTabs;
  };

  const renderActiveTab = () => {
    switch (activeTab) {
      case 'profile':
        return currentUser ? <LearnerProfile userId={currentUser.id} /> : null;
      case 'dashboard':
        return <ContentDashboard />;
      case 'builder':
        return <div className="p-6">Content Builder (Coming Soon)</div>;
      default:
        return <ContentDashboard />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center space-x-4">
              <h1 className="text-xl font-bold text-gray-900">
                Curriculum Builder
              </h1>
              {currentUser && (
                <span className="text-sm text-gray-600">
                  Welcome, {currentUser.first_name} ({currentUser.current_role})
                </span>
              )}
            </div>
            <div className="flex items-center space-x-4">
              {currentUser ? (
                <button
                  onClick={handleSignOut}
                  className="text-sm text-gray-600 hover:text-gray-900"
                >
                  Sign Out
                </button>
              ) : (
                <button
                  onClick={() => setShowSignInModal(true)}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700"
                >
                  Sign In
                </button>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <nav className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex space-x-8">
            {getRoleBasedTabs().map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto">
        {renderActiveTab()}
      </main>

      {/* Sign In Modal */}
      <UserSignInModal
        isOpen={showSignInModal}
        onClose={() => setShowSignInModal(false)}
        onSignIn={handleSignIn}
      />
    </div>
  );
}