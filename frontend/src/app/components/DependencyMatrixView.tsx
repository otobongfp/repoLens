import React from "react";

import { useGraphData } from "../context/GraphDataProvider";

export default function DependencyMatrixView() {
  const { graph } = useGraphData();
  // Guard against invalid graph structure
  if (!graph || !Array.isArray(graph.nodes) || !Array.isArray(graph.edges)) {
    return (
      <div className="text-center text-lg text-primary py-16">
        Invalid graph data
      </div>
    );
  }

  if (!graph)
    return (
      <div className="text-center text-lg text-primary py-16">No data</div>
    );

  // Get all files
  const files = graph.nodes.filter((n: any) => n.type === "file");

  // Build matrix: files x files, true if file A imports file B
  // Also, collect the edge for tooltip
  const matrix = files.map((row: any) =>
    files.map((col: any) => {
      // Find import edges from this file to the target file
      const importEdge = graph.edges.find(
        (e: any) =>
          e.type === "imports" &&
          e.from === row.id &&
          e.to === col.id &&
          e.meta?.local === true
      );

      return importEdge || null;
    })
  );

  const hasAny = matrix.some((row: any) => row.some(Boolean));

  return (
    <div className="py-4 overflow-auto">
      <h2 className="text-xl font-bold text-primary mb-4">Dependency Matrix</h2>
      {!hasAny ? (
        <div className="text-center text-white/70 py-8">
          No file-to-file import dependencies found.
        </div>
      ) : (
        <div className="overflow-auto max-w-full">
          <table className="border-collapse min-w-max text-xs">
            <thead className="sticky top-0 z-10">
              <tr>
                <th className="sticky left-0 z-20 bg-background border-b border-white/10 px-2 py-1 text-left font-bold">
                  File
                </th>
                {files.map((f: any) => (
                  <th
                    key={f.id}
                    className="border-b border-white/10 px-2 py-1 text-white/70 bg-background whitespace-nowrap max-w-[120px] overflow-hidden text-ellipsis sticky top-0"
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
                    className="sticky left-0 z-10 bg-background border-r border-white/10 px-2 py-1 font-bold text-primary whitespace-nowrap max-w-[120px] overflow-hidden text-ellipsis"
                    title={row.path || row.label}
                  >
                    {row.label}
                  </td>
                  {files.map((col: any, j: number) => {
                    const edge = matrix[i][j];
                    let tooltip = "";
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
                        className={`px-2 py-1 text-center border border-white/10 transition-colors duration-150 ${
                          edge
                            ? "bg-primary/40 text-primary font-bold"
                            : "bg-white/5 text-white/60"
                        } hover:bg-primary/20`}
                        title={tooltip}
                      >
                        {edge ? <span className="text-lg">●</span> : ""}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
      <div className="mt-4 text-xs text-white/50">
        ● = File imports dependency. Scroll to explore large matrices. Hover for
        details.
      </div>
    </div>
  );
}
