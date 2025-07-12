'use client';

import { useState } from 'react';
import { buildApiUrl } from '../config/api';

interface User {
  id: number;
  first_name?: string;
  last_name?: string;
  email?: string;
  current_role: string;
}

interface UserSignInModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSignIn: (user: User) => void;
  onCreateAccount: () => void;
}

export default function UserSignInModal({ isOpen, onClose, onSignIn, onCreateAccount }: UserSignInModalProps) {
  const [identifier, setIdentifier] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!identifier.trim()) return;

    setLoading(true);
    setError('');

    try {
      // Use the new sign-in by identifier endpoint
      const response = await fetch(buildApiUrl('users/sign-in/by-identifier'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ identifier: identifier.trim() })
      });
      
      if (response.ok) {
        const signInResponse = await response.json();
        const user = signInResponse.user;

        onSignIn(user);
        onClose();
        setIdentifier('');
      } else if (response.status === 404) {
        setError('User not found. Would you like to create an account?');
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error('Sign-in failed:', error);
      setError('Sign-in failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAccount = () => {
    onClose();
    onCreateAccount();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-96">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-xl font-bold">Sign In</h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            ✕
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Enter your name or email
            </label>
            <input
              type="text"
              value={identifier}
              onChange={(e) => setIdentifier(e.target.value)}
              placeholder="e.g., john.doe@example.com or John Doe"
              className="w-full p-3 border rounded-lg focus:ring-2 focus:ring-blue-500"
              required
            />
          </div>

          {error && (
            <div className="text-red-600 text-sm bg-red-50 p-2 rounded">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="mt-4 pt-4 border-t text-center">
          <p className="text-sm text-gray-600 mb-2">Don't have an account?</p>
          <button
            onClick={handleCreateAccount}
            className="text-blue-600 hover:text-blue-800 text-sm font-medium"
          >
            Create Account
          </button>
        </div>
      </div>
    </div>
  );
}