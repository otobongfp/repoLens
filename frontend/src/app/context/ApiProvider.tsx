/**
 * RepoLens Frontend - Apiprovider Context
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
import React, { createContext, useContext, useEffect, useState } from 'react';

interface ApiContextType {
  apiBase: string;
  useLocalBackend: boolean;
  setUseLocalBackend: (use: boolean) => void;
  isInitialized: boolean;
}

const ApiContext = createContext<ApiContextType>({
  apiBase: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  useLocalBackend: true,
  setUseLocalBackend: () => {},
  isInitialized: false,
});

export const ApiProvider = ({ children }: { children: React.ReactNode }) => {
  const [apiBase, setApiBase] = useState(
    process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
  );
  const [useLocalBackend, setUseLocalBackend] = useState(true);
  const [isInitialized, setIsInitialized] = useState(false);

  // Load preference from localStorage on mount
  useEffect(() => {
    try {
      const savedPreference = localStorage.getItem('useLocalBackend');
      if (savedPreference !== null) {
        const useLocal = JSON.parse(savedPreference);
        setUseLocalBackend(useLocal);
        setApiBase(
          useLocal
            ? process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
            : 'https://api.repolens.org',
        );
        console.log(
          'Loaded API preference from localStorage:',
          useLocal ? 'Local Backend' : 'Cloud API',
        );
      } else {
        // No saved preference, use defaults and save them
        localStorage.setItem('useLocalBackend', JSON.stringify(true));
        console.log('No saved preference, using default: Local Backend');
      }
    } catch (error) {
      console.error('Error loading API preference from localStorage:', error);
      // Fallback to defaults
      localStorage.setItem('useLocalBackend', JSON.stringify(true));
    } finally {
      setIsInitialized(true);
    }
  }, []);

  // Save preference to localStorage
  const handleSetUseLocalBackend = (use: boolean) => {
    try {
      setUseLocalBackend(use);
      setApiBase(
        use
          ? process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
          : 'https://api.repolens.org',
      );
      localStorage.setItem('useLocalBackend', JSON.stringify(use));
      console.log(
        'Saved API preference to localStorage:',
        use ? 'Local Backend' : 'Cloud API',
      );
    } catch (error) {
      console.error('Error saving API preference to localStorage:', error);
    }
  };

  return (
    <ApiContext.Provider
      value={{
        apiBase,
        useLocalBackend,
        setUseLocalBackend: handleSetUseLocalBackend,
        isInitialized,
      }}
    >
      {children}
    </ApiContext.Provider>
  );
};

export const useApi = () => useContext(ApiContext);
