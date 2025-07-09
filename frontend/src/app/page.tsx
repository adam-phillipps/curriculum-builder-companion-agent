'use client';

import { useState } from 'react';
import ContentDashboard from '@/components/ContentDashboard';
import ContentManagement from '@/components/ContentManagement/ContentManagement';
import LearnerProfile from '@/components/LearnerProfile';
import UserSignInModal from '@/components/UserSignInModal';
import CreateAccountModal from '@/components/CreateAccountModal';
import RoleSwitcher from '@/components/RoleSwitcher';

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
  const [showCreateAccountModal, setShowCreateAccountModal] = useState(false);

  const handleSignIn = (user: User) => {
    setCurrentUser(user);
    switch (user.current_role) {
      case 'learner':
        setActiveTab('profile');
        break;
      case 'builder':
        setActiveTab('catalog');
        break;
      case 'curriculum_architect':
        setActiveTab('catalog');
        break;
      case 'admin':
        setActiveTab('catalog');
        break;
      default:
        setActiveTab('catalog');
    }
  };

  const handleAccountCreated = (user: User) => {
    setCurrentUser(user);
    switch (user.current_role) {
      case 'learner':
        setActiveTab('profile');
        break;
      case 'builder':
        setActiveTab('catalog');
        break;
      case 'curriculum_architect':
        setActiveTab('catalog');
        break;
      case 'admin':
        setActiveTab('catalog');
        break;
      default:
        setActiveTab('catalog');
    }
  };

  const handleSignOut = () => {
    setCurrentUser(null);
    setActiveTab('dashboard');
  };

  const handleRoleChange = (newRole: string) => {
    if (currentUser) {
      const updatedUser = { ...currentUser, current_role: newRole };
      setCurrentUser(updatedUser);
      
      // Set appropriate default tab for role
      switch (newRole) {
        case 'learner':
          setActiveTab('profile');
          break;
        case 'builder':
          setActiveTab('builder-profile');
          break;
        case 'curriculum_architect':
          setActiveTab('architect-profile');
          break;
        case 'admin':
          setActiveTab('profile');
          break;
        default:
          setActiveTab('catalog');
      }
    }
  };

  const getRoleBasedTabs = () => {
    if (!currentUser) return [];
    
    const { current_role } = currentUser;
    
    switch (current_role) {
      case 'learner':
        return [
          { id: 'profile', label: 'My Learning Profile' },
          { id: 'catalog', label: 'Content Catalog' }
        ];
      
      case 'builder':
        return [
          { id: 'builder-profile', label: 'Content Builder' },
          { id: 'catalog', label: 'Content Catalog' }
        ];
      
      case 'curriculum_architect':
        return [
          { id: 'architect-profile', label: 'Architect Profile' },
          { id: 'catalog', label: 'Content Catalog' }
        ];
      
      case 'admin':
        return [
          { id: 'profile', label: 'Admin Profile' },
          { id: 'catalog', label: 'Content Catalog' },
          { id: 'admin', label: 'Administration' }
        ];
      
      default:
        return [{ id: 'catalog', label: 'Content Catalog' }];
    }
  };

  const renderActiveTab = () => {
    if (!currentUser) return null;
    
    switch (activeTab) {
      case 'profile':
        return <LearnerProfile userId={currentUser.id} />;
      case 'builder-profile':
        return (
          <div className="container mx-auto px-4 py-8">
            <div className="mb-8">
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                Content Builder
              </h1>
              <p className="text-gray-600">
                Create and submit new learning content
              </p>
            </div>
            <ContentDashboard userRole="builder" />
          </div>
        );
      case 'architect-profile':
        return <div className="p-6 text-center text-gray-600">Curriculum Architect Profile - Coming Soon</div>;

      case 'catalog':
        return (
          <div className="container mx-auto px-4 py-8">
            <div className="mb-8">
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                Content Catalog
              </h1>
              <p className="text-gray-600">
                Browse and manage learning content items
              </p>
            </div>
            <ContentManagement currentUser={currentUser} />
          </div>
        );
      case 'admin':
        return <div className="p-6 text-center text-gray-600">Administration - Coming Soon</div>;
      default:
        return (
          <div className="container mx-auto px-4 py-8">
            <div className="mb-8">
              <h1 className="text-2xl font-bold text-gray-900 mb-2">
                Content Catalog
              </h1>
              <p className="text-gray-600">
                Browse and manage learning content items
              </p>
            </div>
            <ContentManagement currentUser={currentUser} />
          </div>
        );
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
                  Welcome, {currentUser.first_name}
                </span>
              )}
            </div>
            <div className="flex items-center space-x-4">
              {currentUser ? (
                <>
                  <RoleSwitcher 
                    currentUser={currentUser} 
                    onRoleChange={handleRoleChange} 
                  />
                  <button
                    onClick={handleSignOut}
                    className="text-sm text-gray-600 hover:text-gray-900"
                  >
                    Sign Out
                  </button>
                </>
              ) : (
                <>
                  <button
                    onClick={() => setShowCreateAccountModal(true)}
                    className="text-sm text-gray-600 hover:text-gray-900"
                  >
                    Create Account
                  </button>
                  <button
                    onClick={() => setShowSignInModal(true)}
                    className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700"
                  >
                    Sign In
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs - Only show if user is signed in */}
      {currentUser && (
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
      )}

      {/* Main Content */}
      <main className="max-w-7xl mx-auto">
        {renderActiveTab()}
      </main>

      {/* Modals */}
      <UserSignInModal
        isOpen={showSignInModal}
        onClose={() => setShowSignInModal(false)}
        onSignIn={handleSignIn}
        onCreateAccount={() => {
          setShowSignInModal(false);
          setShowCreateAccountModal(true);
        }}
      />

      <CreateAccountModal
        isOpen={showCreateAccountModal}
        onClose={() => setShowCreateAccountModal(false)}
        onAccountCreated={handleAccountCreated}
      />
    </div>
  );
}