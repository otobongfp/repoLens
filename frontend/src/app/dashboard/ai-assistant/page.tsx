'use client';

import Link from 'next/link';
import Navbar from '../../components/Navbar';
import { BotIcon } from '../../components/LucideIcons';

export default function AIAssistantDashboard() {
  return (
    <div className='bg-sidebar flex min-h-screen flex-col'>
      {/* Background Effects */}
      <div className='pointer-events-none absolute inset-0 -z-10'>
        <div className='bg-primary absolute left-[-10%] top-[-10%] h-[400px] w-[400px] rounded-full opacity-20 blur-3xl filter' />
        <div className='absolute bottom-[-10%] right-[-10%] h-[500px] w-[500px] rounded-full bg-blue-400 opacity-15 blur-2xl filter' />
        <div className='absolute left-[60%] top-[30%] h-[300px] w-[300px] rounded-full bg-pink-300 opacity-15 blur-2xl filter' />
      </div>

      <Navbar>
        <Link
          href='/dashboard/select'
          className='text-primary hover:text-primary/80 text-sm font-medium transition-colors'
        >
          ← Back to Features
        </Link>
      </Navbar>

      <main className='flex flex-1 flex-col items-center justify-center px-4 py-8'>
        {/* Coming Soon Content */}
        <div className='max-w-3xl text-center'>
          <div className='mb-6'>
            <BotIcon className='text-primary mx-auto' size={64} />
          </div>
          <h1 className='mb-6 text-4xl font-bold text-white md:text-5xl'>
            Ask the RepoLens AI
          </h1>
          <p className='mb-8 text-xl text-gray-300'>
            Chat with RepoLens AI about repositories and get intelligent
            insights
          </p>

          <div className='mb-8 rounded-xl border border-blue-500/20 bg-blue-500/10 p-6'>
            <h2 className='mb-2 text-2xl font-semibold text-blue-400'>
              AI-Powered Code Analysis
            </h2>
            <p className='mb-4 text-gray-300'>
              This feature will allow you to have natural conversations with
              RepoLens AI about any codebase. Ask questions, get explanations,
              and receive intelligent insights about code structure, patterns,
              and best practices.
            </p>
            <div className='space-y-2 text-left text-sm text-gray-300'>
              <p>
                • <strong>Natural Language Q&A:</strong> Ask questions about
                code in plain English
              </p>
              <p>
                • <strong>Code Explanation:</strong> Get detailed explanations
                of functions, classes, and algorithms
              </p>
              <p>
                • <strong>Best Practices:</strong> Receive suggestions for
                improving code quality
              </p>
              <p>
                • <strong>Security Analysis:</strong> Identify potential
                security issues and vulnerabilities
              </p>
              <p>
                • <strong>Refactoring Suggestions:</strong> Get AI-powered
                recommendations for code improvements
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
