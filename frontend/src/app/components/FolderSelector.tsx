import { useState } from 'react';

interface FolderSelectorProps {
  onFolderSelect: (folderPath: string) => void;
  selectedFolder: string;
}

export default function FolderSelector({
  onFolderSelect,
  selectedFolder,
}: FolderSelectorProps) {
  const [folderPath, setFolderPath] = useState(selectedFolder);
  const [error, setError] = useState('');

  const handleFolderChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const path = e.target.value;
    setFolderPath(path);
    setError('');
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!folderPath.trim()) {
      setError('Please enter a folder path');
      return;
    }
    onFolderSelect(folderPath.trim());
  };

  return (
    <div className='mb-6 w-full max-w-xl rounded-sm bg-white/70 p-4 shadow-sm'>
      <h3 className='mb-3 text-lg font-semibold text-gray-800'>
        Select Folder to Analyze
      </h3>

      <form onSubmit={handleSubmit} className='space-y-3'>
        <div>
          <label
            htmlFor='folderPath'
            className='mb-1 block text-sm font-medium text-gray-700'
          >
            Folder Path
          </label>
          <input
            type='text'
            id='folderPath'
            value={folderPath}
            onChange={handleFolderChange}
            placeholder='Enter folder path (e.g., /Users/username/projects/my-project)'
            className='focus:ring-primary w-full rounded-md border border-gray-300 px-3 py-2 text-gray-800 focus:border-transparent focus:ring-2 focus:outline-hidden'
          />
        </div>

        {error && <p className='text-sm text-red-600'>{error}</p>}

        <button
          type='submit'
          className='bg-primary w-full rounded-md px-4 py-2 text-white transition-colors hover:bg-[#37875e]'
        >
          Validate Folder
        </button>
      </form>

      {selectedFolder && (
        <div className='mt-3 rounded-sm border border-blue-200 bg-blue-50 p-2'>
          <p className='text-sm text-blue-800'>
            <strong>Selected:</strong> {selectedFolder}
          </p>
        </div>
      )}

      <div className='mt-3 text-xs text-gray-600'>
        <p>
          <strong>Examples:</strong>
        </p>
        <ul className='mt-1 list-inside list-disc space-y-1'>
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
