import { useState, useEffect } from "react";
import { useRepolensApi } from "../utils/api";
import { useGraphData } from "../context/GraphDataProvider";
import FolderSelector from "./FolderSelector";

export default function RepoInput() {
  const [selectedFolder, setSelectedFolder] = useState("");
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
      <div className="w-full max-w-xl mb-6">
        <div className="p-4 bg-red-50 border border-red-200 rounded shadow text-center">
          <p className="text-red-600 font-semibold">
            RepoLens Agent Not Connected
          </p>
          <p className="text-red-500 text-sm mt-2">
            Please start the RepoLens agent on port 3090 to analyze
            repositories.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full max-w-xl mb-6">
      <div className="p-4 bg-white/70 rounded shadow text-center mb-4">
        <p className="text-primary font-semibold">
          Connected to local RepoLens Agent
        </p>
        <p className="text-gray-700 text-sm mt-2">
          Select a folder to analyze your local repository.
        </p>
      </div>

      <FolderSelector
        onFolderSelect={setSelectedFolder}
        selectedFolder={selectedFolder}
      />

      {selectedFolder && (
        <div className="flex flex-col items-center gap-2">
          <div className="flex gap-2">
            <button
              onClick={async () => {
                setIsLoading(true);
                setError("");
                setGraph(null);
                setUsingCache(false);
                try {
                  const result = await analyzeRepo("", selectedFolder);
                  setGraph(result.data);
                  setUsingCache(result.fromCache);
                } catch (err) {
                  setError("Failed to analyze folder.");
                } finally {
                  setIsLoading(false);
                }
              }}
              className="px-6 py-3 bg-primary text-white rounded-lg shadow-lg hover:bg-primary/80 transition text-lg font-semibold"
            >
              Analyze Selected Folder
            </button>
            {usingCache && (
              <button
                onClick={async () => {
                  setIsLoading(true);
                  setError("");
                  setGraph(null);
                  setUsingCache(false);
                  try {
                    const result = await analyzeRepo("", selectedFolder);
                    setGraph(result.data);
                    setUsingCache(result.fromCache);
                  } catch (err) {
                    setError("Failed to analyze folder.");
                  } finally {
                    setIsLoading(false);
                  }
                }}
                className="px-4 py-3 bg-orange-500 text-white rounded-lg shadow-lg hover:bg-orange-600 transition text-sm font-semibold"
              >
                Refresh Analysis
              </button>
            )}
          </div>
          {usingCache && (
            <div className="text-sm text-green-600 bg-green-50 px-3 py-1 rounded-full">
              📦 Using cached data
            </div>
          )}
        </div>
      )}
    </div>
  );
}
