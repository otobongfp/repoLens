/**
 * RepoLens Frontend - Visualizationtabs Component
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

import { useState } from 'react';
import GraphView from './GraphView';
import TreeView from './TreeView';
import DependencyMatrixView from './DependencyMatrixView';
import ProjectFlowView from './ProjectFlowView';
import HeatmapView from './HeatmapView';
import { useGraphData } from '../context/GraphDataProvider';

const TABS = [
  { key: 'graph', label: 'Graph View' },
  { key: 'tree', label: 'Tree View' },
  { key: 'matrix', label: 'Dependency Matrix' },
  { key: 'project', label: 'Project Flow' },
  { key: 'heatmap', label: 'Heatmap' },
];

export default function VisualizationTabs() {
  const { graph } = useGraphData();
  const [active, setActive] = useState('graph');

  return (
    <div className='w-full'>
      <div className='mb-4 flex gap-1 overflow-x-auto border-b border-white/10 sm:gap-2'>
        {TABS.map((tab) => (
          <button
            key={tab.key}
            className={`rounded-t px-2 py-2 text-xs font-semibold whitespace-nowrap transition focus:outline-hidden sm:px-4 sm:text-sm ${
              active === tab.key
                ? 'border-primary text-primary border-b-4 bg-white/5'
                : 'text-white/80 hover:bg-white/10'
            }`}
            onClick={() => setActive(tab.key)}
            aria-selected={active === tab.key}
            tabIndex={0}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div className='transition-opacity duration-300'>
        {active === 'graph' && <GraphView />}
        {active === 'tree' && <TreeView />}
        {active === 'matrix' && <DependencyMatrixView />}
        {active === 'project' && <ProjectFlowView />}
        {active === 'heatmap' && <HeatmapView />}
      </div>
    </div>
  );
}
