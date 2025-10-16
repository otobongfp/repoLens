/**
 * RepoLens Frontend - Functionflowview Component
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

import React from 'react';

import { useGraphData } from '../context/GraphDataProvider';

export default function FunctionFlowView() {
  const { graph } = useGraphData();
  // Guard against invalid graph structure
  if (!graph || !Array.isArray(graph.nodes) || !Array.isArray(graph.edges)) {
    return (
      <div className='text-primary py-16 text-center text-lg'>
        Invalid graph data
      </div>
    );
  }

  if (!graph)
    return (
      <div className='text-primary py-16 text-center text-lg'>No data</div>
    );

  // Get all functions
  const functions = graph.nodes.filter((n: any) => n.type === 'function');

  // For each function, find calls edges
  const callsByFunc: Record<
    string,
    { callee: any; edge: any; isExternal: boolean }[]
  > = {};

  functions.forEach((fn: any) => {
    callsByFunc[fn.id] = [];

    // Find all call edges from this function
    const callEdges = graph.edges.filter(
      (e: any) => e.type === 'calls' && e.from === fn.id,
    );

    callEdges.forEach((edge: any) => {
      // Try to find the called function as a node
      const callee = graph.nodes.find(
        (n: any) => n.id === edge.to && n.type === 'function',
      );

      if (callee) {
        // Internal call - function exists in the graph
        callsByFunc[fn.id].push({ callee, edge, isExternal: false });
      } else {
        // External call - function not found in graph (might be external library or not parsed)
        // Extract function name from the edge.to (format: "external:functionName")
        const funcName = edge.to.split(':').pop() || 'unknown';
        callsByFunc[fn.id].push({
          callee: {
            id: edge.to,
            label: funcName,
            type: 'function',
            path: 'external',
            meta: { external: true },
          },
          edge,
          isExternal: true,
        });
      }
    });
  });

  // Get files for context
  const files = graph.nodes.filter((n: any) => n.type === 'file');
  const fileById = files.reduce((acc: any, file: any) => {
    acc[file.id] = file;
    return acc;
  }, {});

  // Find which file contains each function
  const functionFile: Record<string, any> = {};
  functions.forEach((fn: any) => {
    const containsEdge = graph.edges.find(
      (e: any) => e.type === 'contains' && e.to === fn.id,
    );
    if (containsEdge) {
      functionFile[fn.id] = fileById[containsEdge.from];
    }
  });

  const hasAnyCalls = Object.values(callsByFunc).some(
    (calls: any) => calls.length > 0,
  );

  return (
    <div className='py-4'>
      <h2 className='text-primary mb-4 text-xl font-bold'>Function Flow</h2>
      {!hasAnyCalls ? (
        <div className='py-8 text-center text-white/70'>
          No function call relationships found.
        </div>
      ) : (
        <div className='space-y-6'>
          {functions.map((fn: any) => {
            const calls = callsByFunc[fn.id];
            if (calls.length === 0) return null;

            const file = functionFile[fn.id];
            return (
              <div key={fn.id} className='rounded-lg bg-white/5 p-4'>
                <div className='mb-3 flex items-center gap-2'>
                  <span className='text-primary font-bold'>⚡</span>
                  <span className='text-primary font-semibold'>{fn.label}</span>
                  {file && (
                    <span className='text-sm text-white/60'>
                      in {file.label}
                    </span>
                  )}
                </div>
                <div className='ml-6 space-y-2'>
                  {calls.map((call: any, idx: number) => (
                    <div key={idx} className='flex items-center gap-2'>
                      <span className='text-white/40'>→</span>
                      <span
                        className={`${
                          call.isExternal
                            ? 'italic text-purple-400'
                            : 'text-green-400'
                        }`}
                      >
                        {call.callee.label}
                      </span>
                      {call.isExternal && (
                        <span className='text-xs text-white/50'>
                          (external)
                        </span>
                      )}
                      {!call.isExternal && functionFile[call.callee.id] && (
                        <span className='text-sm text-white/60'>
                          in {functionFile[call.callee.id].label}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            );
          })}
        </div>
      )}
      <div className='mt-4 text-xs text-white/50'>
        Shows function call relationships. External calls are shown in purple.
      </div>
    </div>
  );
}
