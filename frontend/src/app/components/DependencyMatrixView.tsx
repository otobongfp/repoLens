/**
 * RepoLens Frontend - Dependencymatrixview Component
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

export default function DependencyMatrixView() {
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

  // Get all files
  const files = graph.nodes.filter((n: any) => n.type === 'file');

  // Build matrix: files x files, true if file A imports file B
  // Also, collect the edge for tooltip
  const matrix = files.map((row: any) =>
    files.map((col: any) => {
      // Find import edges from this file to the target file
      const importEdge = graph.edges.find(
        (e: any) =>
          e.type === 'imports' &&
          e.from === row.id &&
          e.to === col.id &&
          e.meta?.local === true,
      );

      return importEdge || null;
    }),
  );

  const hasAny = matrix.some((row: any) => row.some(Boolean));

  return (
    <div className='overflow-auto py-4'>
      <h2 className='text-primary mb-4 text-xl font-bold'>Dependency Matrix</h2>
      {!hasAny ? (
        <div className='py-8 text-center text-white/70'>
          No file-to-file import dependencies found.
        </div>
      ) : (
        <div className='max-w-full overflow-auto'>
          <table className='min-w-max border-collapse text-xs'>
            <thead className='sticky top-0 z-10'>
              <tr>
                <th className='bg-background sticky left-0 z-20 border-b border-white/10 px-2 py-1 text-left font-bold'>
                  File
                </th>
                {files.map((f: any) => (
                  <th
                    key={f.id}
                    className='bg-background sticky top-0 max-w-[120px] overflow-hidden text-ellipsis whitespace-nowrap border-b border-white/10 px-2 py-1 text-white/70'
                    title={f.path || f.label}
                  >
                    {f.label}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {files.map((row: any, i: number) => (
                <tr key={row.id}>
                  <td
                    className='bg-background text-primary sticky left-0 z-10 max-w-[120px] overflow-hidden text-ellipsis whitespace-nowrap border-r border-white/10 px-2 py-1 font-bold'
                    title={row.path || row.label}
                  >
                    {row.label}
                  </td>
                  {files.map((col: any, j: number) => {
                    const edge = matrix[i][j];
                    let tooltip = '';
                    if (edge) {
                      tooltip = `From: ${row.path || row.label}\nTo: ${
                        col.path || col.label
                      }\nType: Local Import`;
                      if (edge.meta && edge.meta.line) {
                        tooltip += `\nLine: ${edge.meta.line}`;
                      }
                    }
                    return (
                      <td
                        key={col.id}
                        className={`border border-white/10 px-2 py-1 text-center transition-colors duration-150 ${
                          edge
                            ? 'bg-primary/40 text-primary font-bold'
                            : 'bg-white/5 text-white/60'
                        } hover:bg-primary/20`}
                        title={tooltip}
                      >
                        {edge ? <span className='text-lg'>●</span> : ''}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <div className='mt-4 text-xs text-white/50'>
        ● = File imports dependency. Scroll to explore large matrices. Hover for
        details.
      </div>
    </div>
  );
}
