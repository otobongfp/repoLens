/**
 * RepoLens Frontend - Dashboardnavbar Component
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
import { useApi } from '../context/ApiProvider';
import { useAuth } from '../context/AuthProvider';
import UserMenu from './auth/UserMenu';
import AuthModal from './auth/AuthModal';
import { useState } from 'react';

export default function DashboardNavbar() {
  const { useLocalBackend } = useApi();
  const { isAuthenticated, isLoading } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);

  return (
    <>
      <nav className='border-border bg-background fixed z-50 flex h-16 w-full items-center justify-center border px-4 text-white sm:px-6'>
        <section className='flex w-full max-w-5xl items-center justify-between xl:max-w-[1200px]'>
          {/* Left side - API Status takes the logo space */}
          <div className='flex items-center'>
            <span
              className={
                useLocalBackend
                  ? 'rounded-full bg-green-100 px-3 py-1 text-xs font-semibold text-green-800'
                  : 'text-destructive rounded-full bg-red-100 px-3 py-1 text-xs font-semibold'
              }
            >
              {useLocalBackend ? 'Local Backend' : 'Cloud API'}
            </span>
          </div>

          {/* Right side - Profile/Auth */}
          <section className='flex items-center gap-2 sm:gap-4'>
            {isAuthenticated ? (
              <UserMenu />
            ) : (
              <button
                onClick={() => setShowAuthModal(true)}
                className='bg-primary text-primary-foreground hover:bg-primary/90 rounded-lg px-4 py-2 font-semibold transition duration-200'
              >
                Sign In
              </button>
            )}
          </section>
        </section>
      </nav>

      {showAuthModal && <AuthModal onClose={() => setShowAuthModal(false)} />}
    </>
  );
}
