import { useApi } from '../context/ApiProvider';
import { repositoryCache } from './storage';

export function useRepolensApi() {
  const { apiBase, isLocal } = useApi();

  async function analyzeRepo(url: string, folderPath?: string) {
    // Check cache first if we have a folder path
    if (folderPath) {
      const cached = await repositoryCache.get(folderPath);
      if (cached) {
        console.log('Using cached repository analysis');
        return { data: cached, fromCache: true };
      }
    }

    // Use /analyze/project for directory analysis
    const endpoint = folderPath
      ? `${apiBase}/analyze/project`
      : `${apiBase}/analyze`;

    const res = await fetch(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(folderPath ? { folder_path: folderPath } : { url }),
    });
    if (!res.ok) throw new Error('Failed to analyze repo');
    const data = await res.json();

    // Cache the result if we have a folder path
    if (folderPath) {
      try {
        await repositoryCache.set(folderPath, data);
        console.log('Cached repository analysis');
      } catch (error) {
        console.warn('Failed to cache repository analysis:', error);
      }
    }

    return { data, fromCache: false };
  }

  async function getFiles() {
    const res = await fetch(`${apiBase}/files`);
    if (!res.ok) throw new Error('Failed to get files');
    return await res.json();
  }

  async function getFile(path: string) {
    const res = await fetch(`${apiBase}/file?path=${encodeURIComponent(path)}`);
    if (!res.ok) throw new Error('Failed to get file');
    return await res.json();
  }

  // AI endpoint (local FastAPI backend)
  async function askRepoQuestion(graph: any, question: string) {
    const res = await fetch('http://localhost:8000/ai/ask', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ graph_data: graph, question }),
    });
    if (!res.ok) throw new Error('Failed to get answer from AI');
    return await res.json();
  }

  async function fetchEnhancedGraph(folderPath: string) {
    const res = await fetch(`${apiBase}/analyze/enhanced`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ folder_path: folderPath }),
    });
    if (!res.ok) throw new Error('Failed to fetch enhanced graph');
    return await res.json();
  }

  // Cache management functions
  async function clearCache() {
    await repositoryCache.clear();
  }

  async function getCacheStats() {
    return await repositoryCache.getStats();
  }

  async function deleteCachedRepo(folderPath: string) {
    await repositoryCache.delete(folderPath);
  }

  return {
    analyzeRepo,
    getFiles,
    getFile,
    askRepoQuestion,
    fetchEnhancedGraph,
    clearCache,
    getCacheStats,
    deleteCachedRepo,
    apiBase,
    isLocal,
  };
}
