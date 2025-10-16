/**
 * RepoLens Frontend - Treeview Component
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

function renderTree(graph: any) {
  // Group nodes by file
  const files = graph.nodes.filter((n: any) => n.type === 'file');
  const childrenByFile: Record<string, any[]> = {};
  files.forEach((file: any) => {
    childrenByFile[file.id] = graph.nodes.filter(
      (n: any) =>
        (n.type === 'function' || n.type === 'class') &&
        graph.edges.some(
          (e: any) =>
            e.from === file.id && e.to === n.id && e.type === 'contains',
        ),
    );
  });
  return (
    <ul className='pl-4'>
      {files.map((file: any) => (
        <li key={file.id} className='mb-2'>
          <span className='text-primary font-bold'>{file.label}</span>
          <ul className='pl-4'>
            {childrenByFile[file.id].map((child) => (
              <li key={child.id} className='text-white/90'>
                {child.label}{' '}
                <span className='text-xs text-white/50'>({child.type})</span>
              </li>
            ))}
          </ul>
        </li>
      ))}
    </ul>
  );
}

export default function TreeView() {
  const { graph } = useGraphData();

  if (!graph)
    return (
      <div className='text-primary py-16 text-center text-lg'>No data</div>
    );
  return (
    <div className='py-4'>
      <h2 className='text-primary mb-4 text-xl font-bold'>
        Code Structure Tree
      </h2>
      {renderTree(graph)}
    </div>
  );
}
