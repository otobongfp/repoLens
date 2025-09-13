'use client';

import Link from 'next/link';
import Navbar from '../../components/Navbar';
import { PuzzleIcon } from '../../components/LucideIcons';

export default function ComponentsDashboard() {
  return (
    <div className='bg-sidebar flex min-h-screen flex-col'>
      <main className='flex flex-1 flex-col items-center justify-center px-4 py-8'>
        {/* Coming Soon Content */}
        <div className='max-w-3xl text-center'>
          <div className='mb-6'>
            <PuzzleIcon className='text-primary mx-auto' size={64} />
          </div>
          <h1 className='mb-6 text-4xl font-bold text-white md:text-5xl'>
            Dismember Repo into Components
          </h1>
          <p className='mb-8 text-xl text-gray-300'>
            Break down repositories into technologies, algorithms, and create a
            linked learning graph
          </p>

          <div className='mb-8 rounded-xl border border-green-500/20 bg-green-500/10 p-6'>
            <h2 className='mb-2 text-2xl font-semibold text-green-400'>
              Advanced Repository Analysis
            </h2>
            <p className='mb-4 text-gray-300'>
              This feature will provide deep analysis of codebases, breaking
              them down into their fundamental components, identifying
              technologies, algorithms, and creating interconnected learning
              paths.
            </p>
            <div className='space-y-2 text-left text-sm text-gray-300'>
              <p>
                • <strong>Technology Stack Detection:</strong> Automatically
                identify frameworks, libraries, and tools used
              </p>
              <p>
                • <strong>Algorithm Recognition:</strong> Detect and categorize
                algorithms and data structures
              </p>
              <p>
                • <strong>Component Mapping:</strong> Map relationships between
                different parts of the codebase
              </p>
              <p>
                • <strong>Learning Graph Generation:</strong> Create
                interconnected learning paths based on dependencies
              </p>
              <p>
                • <strong>Complexity Analysis:</strong> Identify complex areas
                and suggest learning priorities
              </p>
            </div>
          </div>

          {/* Back to Features */}
          <div className='mt-12'>
            <Link
              href='/dashboard/select'
              className='bg-primary hover:bg-primary/80 inline-flex items-center rounded-lg px-6 py-3 font-semibold text-white transition-colors'
            >
              ← Back to Features
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
