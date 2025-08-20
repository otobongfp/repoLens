import { useState } from "react";

interface FolderSelectorProps {
  onFolderSelect: (folderPath: string) => void;
  selectedFolder: string;
}

export default function FolderSelector({
  onFolderSelect,
  selectedFolder,
}: FolderSelectorProps) {
  const [folderPath, setFolderPath] = useState(selectedFolder);
  const [error, setError] = useState("");

  const handleFolderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const path = e.target.value;
    setFolderPath(path);
    setError("");
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!folderPath.trim()) {
      setError("Please enter a folder path");
      return;
    }
    onFolderSelect(folderPath.trim());
  };

  return (
    <div className="w-full max-w-xl mb-6 p-4 bg-white/70 rounded shadow">
      <h3 className="text-lg font-semibold text-gray-800 mb-3">
        Select Folder to Analyze
      </h3>

      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <label
            htmlFor="folderPath"
            className="block text-sm font-medium text-gray-700 mb-1"
          >
            Folder Path
          </label>
          <input
            type="text"
            id="folderPath"
            value={folderPath}
            onChange={handleFolderChange}
            placeholder="Enter folder path (e.g., /Users/username/projects/my-project)"
            className="w-full px-3 py-2 border border-gray-300 text-gray-800 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
          />
        </div>

        {error && <p className="text-red-600 text-sm">{error}</p>}

        <button
          type="submit"
          className="w-full px-4 py-2 bg-primary text-white rounded-md hover:bg-[#37875e] transition-colors"
        >
          Validate Folder
        </button>
      </form>

      {selectedFolder && (
        <div className="mt-3 p-2 bg-blue-50 border border-blue-200 rounded">
          <p className="text-sm text-blue-800">
            <strong>Selected:</strong> {selectedFolder}
          </p>
        </div>
      )}

      <div className="mt-3 text-xs text-gray-600">
        <p>
          <strong>Examples:</strong>
        </p>
        <ul className="list-disc list-inside space-y-1 mt-1">
          <li>
            Absolute path: <code>/Users/username/projects/my-project</code>
          </li>
          <li>
            Relative path: <code>./src</code> or <code>../parent-folder</code>
          </li>
          <li>
            Home directory: <code>~/Documents/projects</code>
          </li>
        </ul>
      </div>
    </div>
  );
}
