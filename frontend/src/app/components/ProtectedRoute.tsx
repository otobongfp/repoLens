/**
 * RepoLens Frontend - Protectedroute Component
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

import { useAuth } from '../context/AuthProvider';
import AuthModal from './auth/AuthModal';
import LoadingSpinner from './LoadingSpinner';

interface ProtectedRouteProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}

export default function ProtectedRoute({
  children,
  fallback,
}: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className='bg-background flex min-h-screen items-center justify-center'>
        <LoadingSpinner />
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className='bg-background min-h-screen'>
        {fallback || (
          <div className='flex min-h-screen items-center justify-center'>
            <div className='text-center'>
              <h1 className='mb-4 text-2xl font-bold text-white'>
                Authentication Required
              </h1>
              <p className='mb-8 text-gray-400'>
                Please sign in to access this page
              </p>
              <AuthModal />
            </div>
          </div>
        )}
      </div>
    );
  }

  return <>{children}</>;
}
