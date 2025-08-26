import { useState, useEffect } from "react";
import { useRepolensApi } from "../utils/api";

export default function CacheManager() {
  const { getCacheStats, clearCache } = useRepolensApi();
  const [stats, setStats] = useState<{ count: number; size: number } | null>(
    null
  );
  const [loading, setLoading] = useState(false);

  const loadStats = async () => {
    try {
      const cacheStats = await getCacheStats();
      setStats(cacheStats);
    } catch (error) {
      console.error("Failed to load cache stats:", error);
    }
  };

  const handleClearCache = async () => {
    if (
      !confirm("Are you sure you want to clear all cached repository data?")
    ) {
      return;
    }

    setLoading(true);
    try {
      await clearCache();
      await loadStats();
      alert("Cache cleared successfully");
    } catch (error) {
      console.error("Failed to clear cache:", error);
      alert("Failed to clear cache");
    } finally {
      setLoading(false);
    }
  };

  const formatBytes = (bytes: number) => {
    if (bytes === 0) return "0 Bytes";
    const k = 1024;
    const sizes = ["Bytes", "KB", "MB", "GB"];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + " " + sizes[i];
  };

  useEffect(() => {
    loadStats();
  }, []);

  return (
    <div className="fixed bottom-4 right-4 bg-white/90 backdrop-blur-xs rounded-lg shadow-lg border border-gray-200 p-4 max-w-sm">
      <h3 className="font-semibold text-gray-800 mb-2">Cache Manager</h3>

      {stats && (
        <div className="text-sm text-gray-600 mb-3">
          <div>Cached repositories: {stats.count}</div>
          <div>Cache size: {formatBytes(stats.size)}</div>
        </div>
      )}

      <div className="flex gap-2">
        <button
          onClick={loadStats}
          className="px-3 py-1 text-xs bg-gray-200 text-gray-700 rounded-sm hover:bg-gray-300 transition"
        >
          Refresh
        </button>
        <button
          onClick={handleClearCache}
          disabled={loading}
          className="px-3 py-1 text-xs bg-red-500 text-white rounded-sm hover:bg-red-600 transition disabled:opacity-50"
        >
          {loading ? "Clearing..." : "Clear Cache"}
        </button>
      </div>

      <div className="text-xs text-gray-500 mt-2">
        Cache expires after 24 hours
      </div>
    </div>
  );
}
