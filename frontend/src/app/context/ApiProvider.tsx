'use client';
import React, { createContext, useContext, useEffect, useState } from 'react';

interface ApiContextType {
  apiBase: string;
  isLocal: boolean;
}

const ApiContext = createContext<ApiContextType>({
  apiBase: 'http://localhost:3090',
  isLocal: false,
});

export const ApiProvider = ({ children }: { children: React.ReactNode }) => {
  const [apiBase, setApiBase] = useState('http://localhost:3090');
  const [isLocal, setIsLocal] = useState(false);

  useEffect(() => {
    //try to connect to local agent
    fetch('http://localhost:3090/status')
      .then((res) => {
        if (res.ok) {
          setApiBase('http://localhost:3090');
          setIsLocal(true);
        } else {
          setIsLocal(false);
        }
      })
      .catch(() => {
        setIsLocal(false);
      });
  }, []);

  return (
    <ApiContext.Provider value={{ apiBase, isLocal }}>
      {children}
    </ApiContext.Provider>
  );
};

export const useApi = () => useContext(ApiContext);
