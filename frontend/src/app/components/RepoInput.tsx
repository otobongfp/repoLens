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
      <div className='mb-6 w-full max-w-xl'>
        <div className='rounded-sm border border-red-200 bg-red-50 p-4 text-center shadow-sm'>
          <p className='font-semibold text-red-600'>
            RepoLens Agent Not Connected
          </p>
          <p className='mt-2 text-sm text-red-500'>
            Please start the RepoLens agent on port 3090 to analyze
            repositories.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className='mb-6 w-full max-w-xl'>
      <div className='mb-4 rounded-sm bg-white/70 p-4 text-center shadow-sm'>
        <p className='text-primary font-semibold'>
          Connected to local RepoLens Agent
        </p>
        <p className='mt-2 text-sm text-gray-700'>
          Select a folder to analyze your local repository.
        </p>
      </div>

      <FolderSelector
        onFolderSelect={setSelectedFolder}
        selectedFolder={selectedFolder}
      />

      {selectedFolder && (
        <div className='flex flex-col items-center gap-2'>
          <div className='flex gap-2'>
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
              className='bg-primary hover:bg-primary/80 rounded-lg px-6 py-3 text-lg font-semibold text-white shadow-lg transition'
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
                className='rounded-lg bg-orange-500 px-4 py-3 text-sm font-semibold text-white shadow-lg transition hover:bg-orange-600'
              >
                Refresh Analysis
              </button>
            )}
          </div>
          {usingCache && (
            <div className='rounded-full bg-green-50 px-3 py-1 text-sm text-green-600'>
              📦 Using cached data
            </div>
          )}
        </div>
      )}
    </div>
  );
}
