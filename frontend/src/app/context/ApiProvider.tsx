'use client';
import React, { createContext, useContext, useEffect, useState } from 'react';

interface ApiContextType {
  apiBase: string;
  useLocalBackend: boolean;
  setUseLocalBackend: (use: boolean) => void;
}

const ApiContext = createContext<ApiContextType>({
  apiBase: 'https://api.repolens.org',
  useLocalBackend: false,
  setUseLocalBackend: () => {},
});

export const ApiProvider = ({ children }: { children: React.ReactNode }) => {
  const [apiBase, setApiBase] = useState('https://api.repolens.org');
  const [useLocalBackend, setUseLocalBackend] = useState(false);

  // Load preference from localStorage on mount
  useEffect(() => {
    const savedPreference = localStorage.getItem('useLocalBackend');
    if (savedPreference !== null) {
      const useLocal = JSON.parse(savedPreference);
      setUseLocalBackend(useLocal);
      setApiBase(
        useLocal ? 'http://localhost:8000' : 'https://api.repolens.org',
      );
    }
  }, []);

  // Save preference to localStorage
  const handleSetUseLocalBackend = (use: boolean) => {
    setUseLocalBackend(use);
    setApiBase(use ? 'http://localhost:8000' : 'https://api.repolens.org');
    localStorage.setItem('useLocalBackend', JSON.stringify(use));
  };

  return (
    <ApiContext.Provider
      value={{
        apiBase,
        useLocalBackend,
        setUseLocalBackend: handleSetUseLocalBackend,
      }}
    >
      {children}
    </ApiContext.Provider>
  );
};

export const useApi = () => useContext(ApiContext);
