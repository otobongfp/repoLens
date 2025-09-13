import React, { useEffect, useRef, useState } from 'react';
import * as d3 from 'd3';
import { useGraphData } from '../context/GraphDataProvider';

interface ModuleData extends d3.SimulationNodeDatum {
  id: string;
  name: string;
  path: string;
  functions: any[];
  files: any[];
  connections: { to: string; type: string }[];
}

export default function ProjectFlowView() {
  const { graph } = useGraphData();
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);
  const [selectedModule, setSelectedModule] = useState<ModuleData | null>(null);
  const [zoomLevel, setZoomLevel] = useState(1);

  useEffect(() => {
    if (!graph || !svgRef.current || !containerRef.current) return;

    const container = containerRef.current;
    const containerRect = container.getBoundingClientRect();

    // Make SVG responsive to container width
    const width = Math.max(1200, containerRect.width);
    const height = 800;
    const margin = { top: 40, right: 40, bottom: 40, left: 40 };

    const svg = d3.select(svgRef.current);
    svg.selectAll('*').remove();

    // Set SVG dimensions
    svg.attr('width', width).attr('height', height);

    // Create main group for zoom/pan
    const g = svg.append('g');

    // Add zoom behavior
    const zoom = d3
      .zoom()
      .scaleExtent([0.3, 3])
      .on('zoom', (event) => {
        g.attr('transform', event.transform);
        setZoomLevel(event.transform.k);
      });

    svg.call(zoom as any);

    // Group files by modules (directories)
    const modules: ModuleData[] = [];
    const fileToModule: Record<string, string> = {};

    // Get all files and group them by directory
    const files = graph.nodes.filter((n: any) => n.type === 'file');
    const moduleGroups: Record<string, any[]> = {};

    files.forEach((file: any) => {
      if (file.path) {
        const pathParts = file.path.split('/');
        const moduleName = pathParts.length > 1 ? pathParts[0] : 'root';

        if (!moduleGroups[moduleName]) {
          moduleGroups[moduleName] = [];
        }
        moduleGroups[moduleName].push(file);
        fileToModule[file.id] = moduleName;
      }
    });

    // Create module data
    Object.entries(moduleGroups).forEach(([moduleName, moduleFiles]) => {
      const moduleFunctions = graph.nodes.filter(
        (n: any) =>
          n.type === 'function' &&
          moduleFiles.some((f: any) =>
            graph.edges.some(
              (e: any) =>
                e.type === 'contains' && e.from === f.id && e.to === n.id,
            ),
          ),
      );

      // Find connections to other modules
      const connections: { to: string; type: string }[] = [];
      moduleFiles.forEach((file: any) => {
        const importEdges = graph.edges.filter(
          (e: any) =>
            e.type === 'imports' &&
            e.from === file.id &&
            e.meta?.local === true,
        );

        importEdges.forEach((edge: any) => {
          const targetFile = graph.nodes.find((n: any) => n.id === edge.to);
          if (
            targetFile &&
            fileToModule[targetFile.id] &&
            fileToModule[targetFile.id] !== moduleName
          ) {
            connections.push({
              to: fileToModule[targetFile.id],
              type: 'imports',
            });
          }
        });
      });

      modules.push({
        id: moduleName,
        name: moduleName,
        path: moduleName,
        functions: moduleFunctions,
        files: moduleFiles,
        connections: connections,
      });
    });

    if (modules.length === 0) {
      g.append('text')
        .attr('x', width / 2)
        .attr('y', height / 2)
        .attr('text-anchor', 'middle')
        .attr('fill', '#888')
        .text('No modules found');
      return;
    }

    // Create force simulation for layout
    const simulation = d3
      .forceSimulation(modules)
      .force(
        'link',
        d3
          .forceLink()
          .id((d: any) => d.id)
          .distance(200), // Increased distance for better spacing
      )
      .force('charge', d3.forceManyBody().strength(-400))
      .force('center', d3.forceCenter(width / 2, height / 2))
      .force('collision', d3.forceCollide().radius(150)); // Increased collision radius

    // Create connections data
    const connections: any[] = [];
    modules.forEach((module) => {
      module.connections.forEach((conn) => {
        const targetModule = modules.find((m) => m.id === conn.to);
        if (targetModule) {
          connections.push({
            source: module.id,
            target: targetModule.id,
            type: conn.type,
          });
        }
      });
    });

    // Add connections to simulation
    (simulation.force('link') as d3.ForceLink<ModuleData, any>)?.links(
      connections,
    );

    // Create arrow marker
    g.append('defs')
      .append('marker')
      .attr('id', 'arrowhead')
      .attr('viewBox', '0 -5 10 10')
      .attr('refX', 8)
      .attr('refY', 0)
      .attr('markerWidth', 6)
      .attr('markerHeight', 6)
      .attr('orient', 'auto')
      .append('path')
      .attr('d', 'M0,-5L10,0L0,5')
      .attr('fill', '#666');

    // Draw connections
    const link = g
      .append('g')
      .selectAll('path')
      .data(connections)
      .enter()
      .append('path')
      .attr('stroke', '#666')
      .attr('stroke-width', 2)
      .attr('fill', 'none')
      .attr('marker-end', 'url(#arrowhead)')
      .style('stroke-dasharray', '5,5')
      .style('animation', 'flow 2s linear infinite');

    // Create module boxes
    const moduleGroup = g
      .append('g')
      .selectAll('g')
      .data(modules)
      .enter()
      .append('g')
      .style('cursor', 'pointer')
      .on('click', (event, d) => setSelectedModule(d));

    // Module background rectangle
    const moduleRect = moduleGroup
      .append('rect')
      .attr('width', 220) // Slightly wider
      .attr('height', 160) // Slightly taller
      .attr('rx', 8)
      .attr('fill', '#1e293b')
      .attr('stroke', '#475569')
      .attr('stroke-width', 2);

    // Module title
    moduleGroup
      .append('text')
      .attr('x', 110)
      .attr('y', 25)
      .attr('text-anchor', 'middle')
      .attr('fill', '#f59e0b')
      .style('font-size', '14px')
      .style('font-weight', 'bold')
      .text((d: any) => d.name);

    // Module stats
    moduleGroup
      .append('text')
      .attr('x', 110)
      .attr('y', 45)
      .attr('text-anchor', 'middle')
      .attr('fill', '#94a3b8')
      .style('font-size', '11px')
      .text(
        (d: any) => `${d.files.length} files, ${d.functions.length} functions`,
      );

    // Function list (truncated)
    const functionList = moduleGroup
      .append('text')
      .attr('x', 10)
      .attr('y', 65)
      .attr('fill', '#e2e8f0')
      .style('font-size', '10px')
      .style('font-family', 'monospace');

    functionList.each(function (d: any) {
      const functions = d.functions.slice(0, 6); // Show max 6 functions
      const text = d3.select(this);

      functions.forEach((func: any, i: number) => {
        text
          .append('tspan')
          .attr('x', 10)
          .attr('dy', i === 0 ? 0 : '1.2em')
          .text(`• ${func.label}`);
      });

      if (d.functions.length > 6) {
        text
          .append('tspan')
          .attr('x', 10)
          .attr('dy', '1.2em')
          .attr('fill', '#64748b')
          .text(`... and ${d.functions.length - 6} more`);
      }
    });

    // Update positions on simulation tick
    simulation.on('tick', () => {
      link.attr('d', (d: any) => {
        const dx = d.target.x - d.source.x;
        const dy = d.target.y - d.source.y;
        const dr = Math.sqrt(dx * dx + dy * dy);
        return `M${d.source.x},${d.source.y}A${dr},${dr} 0 0,1 ${d.target.x},${d.target.y}`;
      });

      moduleGroup.attr(
        'transform',
        (d: any) => `translate(${d.x - 110},${d.y - 80})`,
      );
    });

    // Add CSS animation
    const style = document.createElement('style');
    style.textContent = `
      @keyframes flow {
        to { stroke-dashoffset: -10; }
      }
    `;
    document.head.appendChild(style);

    // Auto-fit to view after simulation settles
    setTimeout(() => {
      const bounds = g.node()?.getBBox();
      if (bounds) {
        const scale = Math.min(
          (containerRect.width - 100) / bounds.width,
          (height - 100) / bounds.height,
          1,
        );
        const transform = d3.zoomIdentity
          .translate(
            containerRect.width / 2 - (bounds.x + bounds.width / 2) * scale,
            height / 2 - (bounds.y + bounds.height / 2) * scale,
          )
          .scale(scale);
        svg.call(zoom.transform as any, transform);
      }
    }, 1000);
  }, [graph]);

  const resetZoom = () => {
    if (svgRef.current) {
      const svg = d3.select(svgRef.current);
      svg
        .transition()
        .duration(750)
        .call(d3.zoom().transform as any, d3.zoomIdentity);
    }
  };

  const zoomIn = () => {
    if (svgRef.current) {
      const svg = d3.select(svgRef.current);
      svg
        .transition()
        .duration(300)
        .call(d3.zoom().scaleBy as any, 1.3);
    }
  };

  const zoomOut = () => {
    if (svgRef.current) {
      const svg = d3.select(svgRef.current);
      svg
        .transition()
        .duration(300)
        .call(d3.zoom().scaleBy as any, 1 / 1.3);
    }
  };

  return (
    <div className='py-4'>
      <div className='mb-4 flex items-center justify-between'>
        <h2 className='text-primary text-xl font-bold'>Project Flow</h2>

        {/* Zoom controls */}
        <div className='flex items-center gap-2'>
          <span className='text-xs text-white/60'>
            Zoom: {Math.round(zoomLevel * 100)}%
          </span>
          <button
            onClick={zoomOut}
            className='rounded-sm border border-white/20 bg-white/10 px-2 py-1 text-xs hover:bg-white/20'
            title='Zoom Out'
          >
            −
          </button>
          <button
            onClick={resetZoom}
            className='rounded-sm border border-white/20 bg-white/10 px-2 py-1 text-xs hover:bg-white/20'
            title='Reset Zoom'
          >
            ⌂
          </button>
          <button
            onClick={zoomIn}
            className='rounded-sm border border-white/20 bg-white/10 px-2 py-1 text-xs hover:bg-white/20'
            title='Zoom In'
          >
            +
          </button>
        </div>
      </div>

      {/* Selected module details */}
      {selectedModule && (
        <div className='mb-4 rounded-sm border border-white/10 bg-white/5 p-4'>
          <div className='mb-3 flex items-center gap-2'>
            <span className='text-primary font-bold'>📦</span>
            <span className='text-primary font-semibold'>
              {selectedModule.name}
            </span>
            <span className='text-sm text-white/60'>Module</span>
          </div>

          <div className='mb-4 grid grid-cols-2 gap-6'>
            <div>
              <span className='text-white/70'>Files:</span>
              <span className='ml-2 font-bold text-blue-400'>
                {selectedModule.files.length}
              </span>
            </div>
            <div>
              <span className='text-white/70'>Functions:</span>
              <span className='ml-2 font-bold text-green-400'>
                {selectedModule.functions.length}
              </span>
            </div>
            <div>
              <span className='text-white/70'>Connections:</span>
              <span className='ml-2 font-bold text-yellow-400'>
                {selectedModule.connections.length}
              </span>
            </div>
            <div>
              <span className='text-white/70'>Path:</span>
              <span className='ml-2 font-mono text-xs text-white/90'>
                {selectedModule.path}
              </span>
            </div>
          </div>

          {/* Functions list */}
          <div className='mb-3'>
            <h4 className='mb-2 font-semibold text-white/80'>Functions:</h4>
            <div className='grid grid-cols-2 gap-2'>
              {selectedModule.functions.map((func: any) => (
                <div
                  key={func.id}
                  className='rounded-sm bg-white/5 px-2 py-1 text-sm text-white/70'
                >
                  {func.label}
                </div>
              ))}
            </div>
          </div>

          {/* Connections */}
          {selectedModule.connections.length > 0 && (
            <div>
              <h4 className='mb-2 font-semibold text-white/80'>Connections:</h4>
              <div className='flex flex-wrap gap-2'>
                {selectedModule.connections.map((conn, idx) => (
                  <div
                    key={idx}
                    className='rounded-sm bg-white/5 px-2 py-1 text-sm text-white/70'
                  >
                    → {conn.to} ({conn.type})
                  </div>
                ))}
              </div>
            </div>
          )}

          <button
            onClick={() => setSelectedModule(null)}
            className='mt-3 text-xs text-white/50 hover:text-white/70'
          >
            Clear selection
          </button>
        </div>
      )}

      {/* Scrollable container */}
      <div
        ref={containerRef}
        className='bg-background relative overflow-auto rounded-sm border border-white/10'
        style={{ height: '600px' }}
      >
        <svg
          ref={svgRef}
          className='block'
          style={{ minWidth: '100%', minHeight: '100%' }}
        />

        {/* Scroll hint overlay */}
        <div className='absolute right-2 top-2 rounded-sm bg-black/20 px-2 py-1 text-xs text-white/40'>
          Drag to pan • Scroll to zoom
        </div>
      </div>

      <div className='mt-4 text-xs text-white/50'>
        Click on modules to see details. Drag to pan, scroll to zoom. Animated
        arrows show dependencies.
      </div>
    </div>
  );
}
