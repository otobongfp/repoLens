"use client";
import React, { createContext, useContext, useState, useEffect } from "react";
import { repositoryCache } from "../utils/storage";

interface GraphDataContextType {
  graph: any;
  setGraph: (graph: any) => void;
  currentFolder: string;
  setCurrentFolder: (folder: string) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  error: string;
  setError: (error: string) => void;
  fromCache: boolean;
  loadFromCache: (folderPath: string) => Promise<boolean>;
  clearGraph: () => void;
}

const GraphDataContext = createContext<GraphDataContextType>({
  graph: null,
  setGraph: () => {},
  currentFolder: "",
  setCurrentFolder: () => {},
  isLoading: false,
  setIsLoading: () => {},
  error: "",
  setError: () => {},
  fromCache: false,
  loadFromCache: async () => false,
  clearGraph: () => {},
});

export const GraphDataProvider = ({
  children,
}: {
  children: React.ReactNode;
}) => {
  const [graph, setGraph] = useState<any>(null);
  const [currentFolder, setCurrentFolder] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [fromCache, setFromCache] = useState(false);

  // Load the most recently analyzed repository on mount
  useEffect(() => {
    const loadLastRepository = async () => {
      try {
        const stats = await repositoryCache.getStats();
        if (stats.count > 0) {
          // Get the most recent cache entry
          const recentEntry = await repositoryCache.getMostRecent();
          if (recentEntry) {
            setGraph(recentEntry.data);
            setCurrentFolder(recentEntry.folderPath);
            setFromCache(true);
            console.log(
              "Loaded previous repository from cache:",
              recentEntry.folderPath
            );
          }
        }
      } catch (error) {
        console.error("Failed to load last repository:", error);
      }
    };

    loadLastRepository();
  }, []);

  const loadFromCache = async (folderPath: string): Promise<boolean> => {
    try {
      const cached = await repositoryCache.get(folderPath);
      if (cached) {
        setGraph(cached);
        setCurrentFolder(folderPath);
        setFromCache(true);
        setError("");
        return true;
      }
      return false;
    } catch (error) {
      console.error("Failed to load from cache:", error);
      return false;
    }
  };

  const clearGraph = () => {
    setGraph(null);
    setCurrentFolder("");
    setFromCache(false);
    setError("");
  };

  return (
    <GraphDataContext.Provider
      value={{
        graph,
        setGraph,
        currentFolder,
        setCurrentFolder,
        isLoading,
        setIsLoading,
        error,
        setError,
        fromCache,
        loadFromCache,
        clearGraph,
      }}
    >
      {children}
    </GraphDataContext.Provider>
  );
};

export const useGraphData = () => useContext(GraphDataContext);
