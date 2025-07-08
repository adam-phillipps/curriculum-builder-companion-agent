'use client';

import { useState, useEffect } from 'react';
import { api } from '@/lib/api';

interface User {
  id: number;
  first_name?: string;
  last_name?: string;
  current_role: string;
}

interface RoleSwitcherProps {
  currentUser: User;
  onRoleChange: (newRole: string) => void;
}

export default function RoleSwitcher({ currentUser, onRoleChange }: RoleSwitcherProps) {
  const [availableRoles, setAvailableRoles] = useState<string[]>([]);
  const [isOpen, setIsOpen] = useState(false);

  useEffect(() => {
    loadRoles();
  }, []);

  const loadRoles = async () => {
    try {
      const response = await api.get('/users/roles/available');
      setAvailableRoles(response.data);
    } catch (error) {
      console.error('Failed to load roles:', error);
    }
  };

  const handleRoleChange = async (newRole: string) => {
    try {
      await api.post(`/users/${currentUser.id}`, { current_role: newRole });
    } catch (error) {
      console.error('Failed to update role:', error);
    }
    // Update UI regardless (for demo purposes)
    onRoleChange(newRole);
    setIsOpen(false);
  };

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center space-x-2 text-sm text-gray-700 hover:text-gray-900 bg-gray-100 px-3 py-2 rounded-md"
      >
        <span className="capitalize">{currentUser.current_role.replace('_', ' ')}</span>
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>

      {isOpen && (
        <div className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border z-50">
          <div className="py-1">
            {availableRoles.map((role) => (
              <button
                key={role}
                onClick={() => handleRoleChange(role)}
                className={`block w-full text-left px-4 py-2 text-sm hover:bg-gray-100 ${
                  role === currentUser.current_role ? 'bg-blue-50 text-blue-700' : 'text-gray-700'
                }`}
              >
                {role.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}