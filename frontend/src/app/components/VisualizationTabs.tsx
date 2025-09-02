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
      <div className='mb-4 flex gap-2 border-b border-white/10'>
        {TABS.map((tab) => (
          <button
            key={tab.key}
            className={`focus:outline-hidden rounded-t px-4 py-2 font-semibold transition ${
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
