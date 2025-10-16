/**
 * RepoLens Frontend - Authmodal Component
 * 
 * Copyright (C) 2024 RepoLens Contributors
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU Affero General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

'use client';

import { useState } from 'react';
import { useAuth } from '../../context/AuthProvider';
import LoginForm from './LoginForm';
import RegisterForm from './RegisterForm';

interface AuthModalProps {
  onClose?: () => void;
}

export default function AuthModal({ onClose }: AuthModalProps) {
  const { isAuthenticated, isLoading } = useAuth();
  const [isLoginMode, setIsLoginMode] = useState(true);

  // Don't show modal if user is authenticated
  if (isAuthenticated || isLoading) {
    return null;
  }

  return (
    <div className='fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4 backdrop-blur-sm sm:p-8'>
      <div className='relative'>
        <div className='from-primary/20 to-primary/10 absolute inset-0 rounded-3xl bg-gradient-to-r blur-xl'></div>
        <div className='relative'>
          <button
            onClick={onClose}
            className='text-muted-foreground hover:text-foreground absolute top-4 right-4 z-10'
          >
            <svg
              className='h-6 w-6'
              fill='none'
              stroke='currentColor'
              viewBox='0 0 24 24'
            >
              <path
                strokeLinecap='round'
                strokeLinejoin='round'
                strokeWidth={2}
                d='M6 18L18 6M6 6l12 12'
              />
            </svg>
          </button>
          {isLoginMode ? (
            <LoginForm
              onSuccess={() => {
                onClose?.();
              }}
              onSwitchToRegister={() => setIsLoginMode(false)}
            />
          ) : (
            <RegisterForm
              onSuccess={() => {
                onClose?.();
              }}
              onSwitchToLogin={() => setIsLoginMode(true)}
            />
          )}
        </div>
      </div>
    </div>
  );
}
