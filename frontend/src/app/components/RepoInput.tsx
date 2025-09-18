import { useState, useEffect } from 'react';
import { useRepolensApi } from '../utils/api';
import { useGraphData } from '../context/GraphDataProvider';
import FolderSelector from './FolderSelector';

interface RepoInputProps {
  onAnalyze?: (folderPath: string) => Promise<void>;
}

export default function RepoInput({ onAnalyze }: RepoInputProps = {}) {
  const [selectedFolder, setSelectedFolder] = useState('');
  const [usingCache, setUsingCache] = useState(false);
  const { isLocal, analyzeRepo } = useRepolensApi();
  const { setGraph, setIsLoading, setError, currentFolder, fromCache } =
    useGraphData();

  // Update selected folder when current folder changes (from cache)
  useEffect(() => {
    if (currentFolder) {
      setSelectedFolder(currentFolder);
      setUsingCache(fromCache);
    }
  }, [currentFolder, fromCache]);

  if (!isLocal) {
    return (
      <div className='mb-6 w-full max-w-xl px-4 sm:px-0'>
        <div className='rounded-sm border border-red-200 bg-red-50 p-4 text-center shadow-sm'>
          <p className='text-sm font-semibold text-red-600 sm:text-base'>
            RepoLens Agent Not Connected
          </p>
          <p className='mt-2 text-xs text-red-500 sm:text-sm'>
            Please start the RepoLens agent on port 3090 to analyze
            repositories.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className='mb-6 w-full max-w-xl px-4 sm:px-0'>
      <div className='mb-4 rounded-sm bg-white/70 p-4 text-center shadow-sm'>
        <p className='text-primary text-sm font-semibold sm:text-base'>
          Connected to local RepoLens Agent
        </p>
        <p className='mt-2 text-xs text-gray-700 sm:text-sm'>
          Select a folder to analyze your local repository.
        </p>
      </div>

      <FolderSelector
        onFolderSelect={setSelectedFolder}
        selectedFolder={selectedFolder}
      />

      {selectedFolder && (
        <div className='flex flex-col items-center gap-2'>
          <div className='flex w-full flex-col gap-2 sm:w-auto sm:flex-row'>
            <button
              onClick={async () => {
                if (onAnalyze) {
                  await onAnalyze(selectedFolder);
                } else {
                  setIsLoading(true);
                  setError('');
                  setGraph(null);
                  setUsingCache(false);
                  try {
                    const result = await analyzeRepo('', selectedFolder);
                    setGraph(result.data);
                    setUsingCache(result.fromCache);
                  } catch (err) {
                    setError('Failed to analyze folder.');
                  } finally {
                    setIsLoading(false);
                  }
                }
              }}
              className='bg-primary hover:bg-primary/80 w-full rounded-lg px-4 py-2 text-sm font-semibold text-white shadow-lg transition sm:w-auto sm:px-6 sm:py-3 sm:text-lg'
            >
              {onAnalyze
                ? 'Start Enhanced Analysis'
                : 'Analyze Selected Folder'}
            </button>
            {usingCache && (
              <button
                onClick={async () => {
                  setIsLoading(true);
                  setError('');
                  setGraph(null);
                  setUsingCache(false);
                  try {
                    const result = await analyzeRepo('', selectedFolder);
                    setGraph(result.data);
                    setUsingCache(result.fromCache);
                  } catch (err) {
                    setError('Failed to analyze folder.');
                  } finally {
                    setIsLoading(false);
                  }
                }}
                className='w-full rounded-lg bg-orange-500 px-4 py-2 text-sm font-semibold text-white shadow-lg transition hover:bg-orange-600 sm:w-auto sm:py-3'
              >
                Refresh Analysis
              </button>
            )}
          </div>
          {usingCache && (
            <div className='rounded-full bg-green-50 px-3 py-1 text-xs text-green-600 sm:text-sm'>
              📦 Using cached data
            </div>
          )}
        </div>
      )}
    </div>
  );
}
