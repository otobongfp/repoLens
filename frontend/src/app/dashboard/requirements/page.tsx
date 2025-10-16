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

export const runtime = 'edge';

export default function RequirementsPage() {
  return (
    <div className='flex min-h-[60vh] flex-col items-center justify-center'>
      {/* Header */}
      <div className='mb-8 text-center'>
        <h1 className='text-foreground mb-2 font-serif text-3xl font-bold tracking-tighter md:text-4xl'>
          Match Requirements to Codebase
        </h1>
        <p className='text-muted-foreground max-w-xl text-sm md:text-base'>
          Analyze how well code meets specific requirements and outline gaps,
          timelines, resource planning, etc.
        </p>
      </div>

      {/* Coming Soon Content */}
      <div className='max-w-3xl text-center'>
        <div className='mb-6 text-6xl'>🎯</div>

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
              • <strong>Timeline Prediction:</strong> Generate realistic project
              timelines using historical data and complexity analysis
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
              • <strong>Risk Assessment:</strong> Evaluate potential challenges
              and bottlenecks in implementation
            </p>
          </div>
        </div>

        {/* Feature Preview */}
        <div className='mt-12 grid grid-cols-1 gap-6 md:grid-cols-2'>
          <div className='rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-md'>
            <div className='mb-3 text-3xl'>📋</div>
            <h3 className='mb-2 text-lg font-semibold text-white'>
              Requirements Analysis
            </h3>
            <p className='text-sm text-gray-300'>
              Upload requirements documents and automatically map them to
              existing codebase components
            </p>
          </div>

          <div className='rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-md'>
            <div className='mb-3 text-3xl'>⏱️</div>
            <h3 className='mb-2 text-lg font-semibold text-white'>
              Timeline Estimation
            </h3>
            <p className='text-sm text-gray-300'>
              Get accurate project timelines based on codebase complexity and
              requirement scope
            </p>
          </div>

          <div className='rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-md'>
            <div className='mb-3 text-3xl'>👥</div>
            <h3 className='mb-2 text-lg font-semibold text-white'>
              Resource Planning
            </h3>
            <p className='text-sm text-gray-300'>
              Identify required team skills and optimal resource allocation for
              project success
            </p>
          </div>

          <div className='rounded-xl border border-white/10 bg-white/5 p-6 backdrop-blur-md'>
            <div className='mb-3 text-3xl'>⚠️</div>
            <h3 className='mb-2 text-lg font-semibold text-white'>
              Risk Assessment
            </h3>
            <p className='text-sm text-gray-300'>
              Evaluate potential challenges and bottlenecks before project
              implementation
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
