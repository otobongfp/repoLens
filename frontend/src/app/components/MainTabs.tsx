/**
 * RepoLens Frontend - Maintabs Component
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

import React, { useState } from 'react';
import VisualizationTabs from './VisualizationTabs';
import AIAnalysisView from './AIAnalysisView';
import { useGraphData } from '../context/GraphDataProvider';

export default function MainTabs() {
  const { graph } = useGraphData();
  const [activeMode, setActiveMode] = useState<'visualization' | 'ai-analysis'>(
    'visualization',
  );

  return (
    <div className='w-full'>
      {/* Main Mode Tabs */}
      <div className='mb-4 flex gap-1 overflow-x-auto border-b border-white/10 sm:mb-6 sm:gap-2'>
        <button
          className={`rounded-t px-3 py-2 text-sm font-semibold whitespace-nowrap transition focus:outline-hidden sm:px-6 sm:py-3 sm:text-base ${
            activeMode === 'visualization'
              ? 'border-primary text-primary border-b-4 bg-white/5'
              : 'text-white/80 hover:bg-white/10'
          }`}
          onClick={() => setActiveMode('visualization')}
        >
          📊 Visualization
        </button>
        <button
          className={`rounded-t px-3 py-2 text-sm font-semibold whitespace-nowrap transition focus:outline-hidden sm:px-6 sm:py-3 sm:text-base ${
            activeMode === 'ai-analysis'
              ? 'border-primary text-primary border-b-4 bg-white/5'
              : 'text-white/80 hover:bg-white/10'
          }`}
          onClick={() => setActiveMode('ai-analysis')}
        >
          🤖 AI Analysis
        </button>
      </div>

      {/* Content */}
      <div className='transition-opacity duration-300'>
        {activeMode === 'visualization' && <VisualizationTabs />}
        {activeMode === 'ai-analysis' && <AIAnalysisView />}
      </div>
    </div>
  );
}
