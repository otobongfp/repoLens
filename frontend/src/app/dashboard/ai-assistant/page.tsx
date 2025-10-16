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

import { useState } from 'react';
import toast from 'react-hot-toast';
import { useGraphData } from '../../context/GraphDataProvider';
import { useRepolensApi } from '../../utils/api';

export default function AIAssistantPage() {
  const { graph } = useGraphData();
  const { askRepoQuestion } = useRepolensApi();
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleAskQuestion = async () => {
    if (!question.trim() || !graph) return;

    setLoading(true);
    setError('');
    setAnswer('');

    try {
      const result = await askRepoQuestion(graph, question);
      if (result.error) {
        setError(result.error);
        toast.error('Failed to get answer from AI');
      } else {
        setAnswer(result.answer);
        toast.success('AI response received');
      }
    } catch (err) {
      setError('Failed to get answer from AI');
      toast.error('Failed to get answer from AI');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className='flex min-h-[60vh] flex-col items-center justify-center'>
      {/* Header */}
      <div className='mb-8 text-center'>
        <h1 className='text-foreground mb-2 font-serif text-3xl font-bold tracking-tighter md:text-4xl'>
          Ask RepoLens AI
        </h1>
        <p className='text-muted-foreground max-w-xl text-sm md:text-base'>
          Chat with RepoLens AI about the repo and its inner workings
        </p>
      </div>

      {/* Chat Interface */}
      <div className='w-full max-w-4xl'>
        {!graph ? (
          <div className='text-center'>
            <div className='mb-4 text-6xl'>🤖</div>
            <h3 className='text-foreground mb-2 text-xl font-semibold'>
              No Repository Loaded
            </h3>
            <p className='text-muted-foreground text-sm'>
              Please analyze a repository first to start asking questions
            </p>
          </div>
        ) : (
          <div className='space-y-6'>
            {/* Question Input */}
            <div className='rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-md'>
              <div className='mb-4'>
                <label
                  htmlFor='question'
                  className='text-foreground mb-2 block text-sm font-medium'
                >
                  Ask a question about the codebase
                </label>
                <textarea
                  id='question'
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                  placeholder='e.g., How does the authentication system work? What are the main components of this application?'
                  className='focus:border-primary w-full rounded-lg border border-white/10 bg-white/5 p-3 text-sm text-white placeholder-gray-400 focus:outline-none'
                  rows={3}
                />
              </div>
              <button
                onClick={handleAskQuestion}
                disabled={!question.trim() || loading}
                className='bg-primary hover:bg-primary/80 rounded-lg px-6 py-2 text-sm font-semibold text-white transition disabled:cursor-not-allowed disabled:opacity-50'
              >
                {loading ? 'Asking...' : 'Ask AI'}
              </button>
            </div>

            {/* Answer Display */}
            {(answer || error) && (
              <div className='rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-md'>
                <h3 className='text-foreground mb-4 text-lg font-semibold'>
                  AI Response
                </h3>
                {error ? (
                  <div className='rounded-lg border border-red-500/30 bg-red-500/10 p-4'>
                    <p className='text-red-300'>{error}</p>
                  </div>
                ) : (
                  <div className='prose prose-invert max-w-none'>
                    <p className='whitespace-pre-wrap text-gray-300'>
                      {answer}
                    </p>
                  </div>
                )}
              </div>
            )}

            {/* Loading State */}
            {loading && (
              <div className='rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-md'>
                <div className='flex items-center justify-center'>
                  <div className='border-primary mr-3 h-6 w-6 animate-spin rounded-full border-b-2'></div>
                  <p className='text-gray-400'>AI is thinking...</p>
                </div>
              </div>
            )}

            {/* Example Questions */}
            <div className='rounded-2xl border border-white/10 bg-white/5 p-6 backdrop-blur-md'>
              <h3 className='text-foreground mb-4 text-lg font-semibold'>
                Example Questions
              </h3>
              <div className='grid grid-cols-1 gap-3 md:grid-cols-2'>
                {[
                  'What is the main architecture of this application?',
                  'How does the authentication system work?',
                  'What are the main dependencies and libraries used?',
                  'How is data stored and retrieved?',
                  'What are the main API endpoints?',
                  'How does error handling work in this codebase?',
                ].map((example, index) => (
                  <button
                    key={index}
                    onClick={() => setQuestion(example)}
                    className='rounded-lg border border-white/10 bg-white/5 p-3 text-left text-sm text-gray-300 transition hover:bg-white/10'
                  >
                    {example}
                  </button>
                ))}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
