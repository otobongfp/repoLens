/**
 * RepoLens Frontend - Page Component
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
            Match Requirements to Codebase
          </h1>
          <p className='mb-8 text-xl text-gray-300'>
            Analyze how well codebases meet specific requirements and provide
            implementation estimates, timelines, and resource planning for
            software development projects.
          </p>

          <div className='mb-8 rounded-xl border border-green-500/20 bg-green-500/10 p-6'>
            <h2 className='mb-2 text-2xl font-semibold text-green-400'>
              Requirements-Codebase Matching Analysis
            </h2>
            <p className='mb-4 text-gray-300'>
              This feature provides intelligent analysis of how well existing
              codebases align with specific requirements, enabling accurate
              project estimation, timeline planning, and resource allocation for
              software development projects.
            </p>
            <div className='space-y-2 text-left text-sm text-gray-300'>
              <p>
                • <strong>Requirements Mapping:</strong> Match functional and
                non-functional requirements to existing codebase components
              </p>
              <p>
                • <strong>Implementation Estimation:</strong> Calculate effort
                estimates based on codebase complexity and requirement scope
              </p>
              <p>
                • <strong>Timeline Prediction:</strong> Generate realistic
                project timelines using historical data and complexity analysis
              </p>
              <p>
                • <strong>Resource Planning:</strong> Identify required skills,
                team size, and resource allocation for successful implementation
              </p>
              <p>
                • <strong>Gap Analysis:</strong> Identify missing components and
                suggest development priorities
              </p>
              <p>
                • <strong>Risk Assessment:</strong> Evaluate potential
                challenges and bottlenecks in implementation
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
