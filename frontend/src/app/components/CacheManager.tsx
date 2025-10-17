import { useState, useEffect } from 'react';
import { useRepolensApi } from '../utils/api';

export default function CacheManager() {
  const { getCacheStats, clearCache } = useRepolensApi();
  const [stats, setStats] = useState<{ count: number; size: number } | null>(
    null,
  );
  const [loading, setLoading] = useState(false);

  const loadStats = async () => {
    try {
      const cacheStats = await getCacheStats();
      setStats(cacheStats);
    } catch (error) {
      console.error('Failed to load cache stats:', error);
    }
  };

  const handleClearCache = async () => {
    if (
      !confirm('Are you sure you want to clear all cached repository data?')
    ) {
      return;
    }

    setLoading(true);
    try {
      await clearCache();
      await loadStats();
      alert('Cache cleared successfully');
    } catch (error) {
      console.error('Failed to clear cache:', error);
      alert('Failed to clear cache');
    } finally {
      setLoading(false);
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  useEffect(() => {
    loadStats();
  }, []);

  return (
    <div className='backdrop-blur-xs fixed bottom-4 right-4 max-w-sm rounded-lg border border-gray-200 bg-white/90 p-4 shadow-lg'>
      <h3 className='mb-2 font-semibold text-gray-800'>Cache Manager</h3>

      {stats && (
        <div className='mb-3 text-sm text-gray-600'>
          <div>Cached repositories: {stats.count}</div>
          <div>Cache size: {formatBytes(stats.size)}</div>
        </div>
      )}

      <div className='flex gap-2'>
        <button
          onClick={loadStats}
          className='rounded-sm bg-gray-200 px-3 py-1 text-xs text-gray-700 transition hover:bg-gray-300'
        >
          Refresh
        </button>
        <button
          onClick={handleClearCache}
          disabled={loading}
          className='rounded-sm bg-red-500 px-3 py-1 text-xs text-white transition hover:bg-red-600 disabled:opacity-50'
        >
          {loading ? 'Clearing...' : 'Clear Cache'}
        </button>
      </div>

      <div className='mt-2 text-xs text-gray-500'>
        Cache expires after 24 hours
      </div>
    </div>
  );
}
