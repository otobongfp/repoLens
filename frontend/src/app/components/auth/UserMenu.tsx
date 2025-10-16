/**
 * RepoLens Frontend - Usermenu Component
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

import { useAuth } from '../../context/AuthProvider';
import { useState } from 'react';

export default function UserMenu() {
  const { user, logout } = useAuth();
  const [isOpen, setIsOpen] = useState(false);

  if (!user) return null;

  const handleLogout = async () => {
    try {
      await logout();
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return (
    <div className='relative'>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className='text-foreground hover:text-muted-foreground flex items-center space-x-3 transition-colors'
      >
        {user.avatar_url ? (
          <img
            src={user.avatar_url}
            alt={user.full_name || user.email}
            className='h-8 w-8 rounded-full'
          />
        ) : (
          <div className='bg-primary flex h-8 w-8 items-center justify-center rounded-full'>
            <span className='text-primary-foreground text-sm font-semibold'>
              {(user.full_name || user.email).charAt(0).toUpperCase()}
            </span>
          </div>
        )}
        <div className='text-left'>
          <div className='text-sm font-medium'>
            {user.full_name || user.email}
          </div>
          <div className='text-muted-foreground text-xs'>{user.role}</div>
        </div>
        <svg
          className={`h-4 w-4 transition-transform ${isOpen ? 'rotate-180' : ''}`}
          fill='none'
          stroke='currentColor'
          viewBox='0 0 24 24'
        >
          <path
            strokeLinecap='round'
            strokeLinejoin='round'
            strokeWidth={2}
            d='M19 9l-7 7-7-7'
          />
        </svg>
      </button>

      {isOpen && (
        <div className='border-border bg-card/95 absolute right-0 z-50 mt-2 w-48 rounded-lg border py-2 backdrop-blur-md'>
          <div className='border-border border-b px-4 py-2'>
            <div className='text-card-foreground text-sm font-medium'>
              {user.full_name || 'User'}
            </div>
            <div className='text-muted-foreground text-xs'>{user.email}</div>
          </div>

          <button
            onClick={handleLogout}
            className='text-destructive hover:bg-accent w-full px-4 py-2 text-left text-sm transition-colors'
          >
            Sign out
          </button>
        </div>
      )}
    </div>
  );
}
