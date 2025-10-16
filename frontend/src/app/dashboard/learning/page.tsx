/**
 * RepoLens Frontend - Page
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

export default function LearningDashboard() {
  return (
    <div className='bg-sidebar flex min-h-screen flex-col'>
      <main className='flex flex-1 flex-col items-center justify-center px-4 py-8'>
        {/* Coming Soon Content */}
        <div className='max-w-2xl text-center'>
          <div className='mb-6 text-6xl'>🎓</div>
          <h1 className='mb-6 text-4xl font-bold text-white md:text-5xl'>
            Micro-Learning
          </h1>
          <p className='mb-8 text-xl text-gray-300'>
            Pick a path, assess your knowledge, and follow a curated journey
            through code.
          </p>

          <div className='mb-8 rounded-xl border border-orange-500/20 bg-orange-500/10 p-6'>
            <h2 className='mb-2 text-2xl font-semibold text-orange-400'>
              Coming Soon
            </h2>
            <p className='text-gray-300'>
              We're building an intelligent learning system that will help you
              master code through personalized paths and assessments.
            </p>
          </div>

          {/* Feature Preview */}
          <div className='mt-12 grid grid-cols-1 gap-6 md:grid-cols-2'>
            <div className='rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-md'>
              <div className='mb-3 text-3xl'>📊</div>
              <h3 className='mb-2 text-lg font-semibold text-white'>
                Knowledge Assessment
              </h3>
              <p className='text-sm text-gray-300'>
                Take quizzes to assess your current knowledge and identify
                learning gaps
              </p>
            </div>

            <div className='rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-md'>
              <div className='mb-3 text-3xl'>🛤️</div>
              <h3 className='mb-2 text-lg font-semibold text-white'>
                Learning Paths
              </h3>
              <p className='text-sm text-gray-300'>
                Follow curated learning paths based on your goals and current
                skill level
              </p>
            </div>

            <div className='rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-md'>
              <div className='mb-3 text-3xl'>🎯</div>
              <h3 className='mb-2 text-lg font-semibold text-white'>
                Progress Tracking
              </h3>
              <p className='text-sm text-gray-300'>
                Track your learning progress and celebrate milestones
              </p>
            </div>

            <div className='rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-md'>
              <div className='mb-3 text-3xl'>🤝</div>
              <h3 className='mb-2 text-lg font-semibold text-white'>
                Community Learning
              </h3>
              <p className='text-sm text-gray-300'>
                Learn with others and share knowledge in a collaborative
                environment
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
