'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';

interface User {
  id: number;
  first_name?: string;
  last_name?: string;
  current_role: string;
}

interface UserSignInModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSignIn: (user: User) => void;
}

export default function UserSignInModal({ isOpen, onClose, onSignIn }: UserSignInModalProps) {
  const [users, setUsers] = useState<User[]>([]);
  const [availableRoles, setAvailableRoles] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (isOpen) {
      loadData();
    }
  }, [isOpen]);

  const loadData = async () => {
    setLoading(true);
    try {
      const [usersResponse, rolesResponse] = await Promise.all([
        api.get('/users/'),
        api.get('/users/roles/available')
      ]);
      setUsers(usersResponse.data);
      setAvailableRoles(rolesResponse.data);
    } catch (error) {
      console.error('Failed to load data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSignIn = async (userId: number) => {
    try {
      const response = await api.post('/users/sign-in', { user_id: userId });
      onSignIn(response.data.user);
      onClose();
    } catch (error) {
      console.error('Sign-in failed:', error);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-96 max-h-96 overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Select User</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            ✕
          </button>
        </div>

        {loading ? (
          <div className="text-center py-4">Loading...</div>
        ) : (
          <div className="space-y-2">
            {users.map((user) => (
              <button
                key={user.id}
                onClick={() => handleSignIn(user.id)}
                className="w-full text-left p-3 border rounded hover:bg-gray-50 transition-colors"
              >
                <div className="font-medium">
                  {user.first_name} {user.last_name}
                </div>
                <div className="text-sm text-gray-600 capitalize">
                  {user.current_role}
                </div>
              </button>
            ))}
          </div>
        )}

        <div className="mt-4 pt-4 border-t">
          <div className="text-sm text-gray-600">
            Available roles: {availableRoles.join(', ')}
          </div>
        </div>
      </div>
    </div>
  );
}