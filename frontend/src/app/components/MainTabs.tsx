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
      <div className='mb-6 flex gap-2 border-b border-white/10'>
        <button
          className={`focus:outline-hidden rounded-t px-6 py-3 font-semibold transition ${
            activeMode === 'visualization'
              ? 'border-primary text-primary border-b-4 bg-white/5'
              : 'text-white/80 hover:bg-white/10'
          }`}
          onClick={() => setActiveMode('visualization')}
        >
          📊 Visualization
        </button>
        <button
          className={`focus:outline-hidden rounded-t px-6 py-3 font-semibold transition ${
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
