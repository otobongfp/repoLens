/**
 * RepoLens Frontend - Repoinput Component
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
  const { analyzeRepo, analyzeRepoFresh } = useRepolensApi();
  const {
    setGraph,
    setIsLoading,
    setError,
    currentFolder,
    fromCache,
    setCurrentFolder,
    clearGraph,
    isLoading,
  } = useGraphData();

  useEffect(() => {
    if (currentFolder) {
      setSelectedFolder(currentFolder);
      setUsingCache(fromCache);
    }
  }, [currentFolder, fromCache]);

  useEffect(() => {
    if (selectedFolder && selectedFolder !== currentFolder) {
      setUsingCache(false);
      setError('');
    }
  }, [selectedFolder, currentFolder]);

  return (
    <div className='w-full'>
      <div className='mb-6 rounded-lg border border-white/10 bg-white/5 p-4 text-center backdrop-blur-sm'>
        <p className='text-primary text-sm font-semibold sm:text-base'>
          Repository Analysis Ready
        </p>
        <p className='text-muted-foreground mt-2 text-xs sm:text-sm'>
          Select a folder to analyze your local repository.
        </p>
      </div>

      <FolderSelector
        onFolderSelect={setSelectedFolder}
        selectedFolder={selectedFolder}
      />

      {selectedFolder && (
        <div className='mt-6 flex flex-col items-center gap-4'>
          <div className='flex w-full flex-col gap-3 sm:w-auto sm:flex-row'>
            <button
              onClick={async () => {
                if (isLoading) {
                  return;
                }

                if (onAnalyze) {
                  await onAnalyze(selectedFolder);
                } else {
                  clearGraph();
                  setIsLoading(true);
                  setError('');
                  setUsingCache(false);
                  try {
                    const result = await analyzeRepoFresh('', selectedFolder);
                    setGraph(result.data);
                    setCurrentFolder(selectedFolder);
                    setUsingCache(result.fromCache);
                  } catch (err) {
                    console.error('Analysis failed:', err);
                    setError('Failed to analyze folder.');
                  } finally {
                    setIsLoading(false);
                  }
                }
              }}
              className='bg-primary hover:bg-primary/80 w-full rounded-lg px-6 py-3 text-sm font-semibold text-white shadow-lg transition sm:w-auto sm:text-base'
            >
              {onAnalyze
                ? 'Start Enhanced Analysis'
                : 'Analyze Selected Folder'}
            </button>
            {usingCache && (
              <button
                onClick={async () => {
                  clearGraph();
                  setIsLoading(true);
                  setError('');
                  setUsingCache(false);
                  try {
                    const result = await analyzeRepoFresh('', selectedFolder);
                    setGraph(result.data);
                    setCurrentFolder(selectedFolder);
                    setUsingCache(result.fromCache);
                  } catch (err) {
                    setError('Failed to analyze folder.');
                  } finally {
                    setIsLoading(false);
                  }
                }}
                className='w-full rounded-lg bg-orange-500 px-6 py-3 text-sm font-semibold text-white shadow-lg transition hover:bg-orange-600 sm:w-auto sm:text-base'
              >
                Refresh Analysis
              </button>
            )}
          </div>
          {usingCache && (
            <div className='rounded-full border border-green-500/30 bg-green-500/20 px-4 py-2 text-xs text-green-300 sm:text-sm'>
              📦 Using cached data
            </div>
          )}
        </div>
      )}
    </div>
  );
}
