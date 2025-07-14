import React from "react";

export default function DependencyMatrixView({ graph }: { graph: any }) {
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

  // Helper function to resolve import path to actual file path
  const resolveImportPath = (importPath: string, sourceFile: string) => {
    if (!importPath || !sourceFile) return importPath;

    if (importPath.startsWith(".")) {
      // Relative import - resolve from source file
      const sourceDir = sourceFile.split("/").slice(0, -1).join("/");
      const resolvedPath = importPath
        .replace(/^\.\//, `${sourceDir}/`)
        .replace(/^\.\.\//, `${sourceDir.split("/").slice(0, -1).join("/")}/`);

      // Try to match with .ts extension
      if (!resolvedPath.endsWith(".ts") && !resolvedPath.endsWith(".tsx")) {
        return `${resolvedPath}.ts`;
      }
      return resolvedPath;
    }
    // External package - return as is
    return importPath;
  };

  // Build matrix: files x files, true if file A imports file B
  // Also, collect the edge for tooltip
  const matrix = files.map((row: any) =>
    files.map((col: any) => {
      // Find import edges from this file
      const importEdges = graph.edges.filter(
        (e: any) => e.type === "imports" && e.from === row.id
      );

      // Check if any of these imports resolve to the target file
      for (const edge of importEdges) {
        const importNode = graph.nodes.find(
          (n: any) => n.id === edge.to && n.type === "import"
        );
        if (importNode && importNode.meta) {
          const resolvedPath = resolveImportPath(
            importNode.meta.imported_module,
            importNode.meta.source_file
          );

          // Check if resolved path matches target file path
          if (
            resolvedPath === col.path ||
            resolvedPath.endsWith(col.label) ||
            col.path.endsWith(
              importNode.meta.imported_module
                .replace(/^\.\//, "")
                .replace(/^\.\.\//, "")
            )
          ) {
            return edge;
          }
        }
      }
      return null;
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
                      // Find the import node
                      const importNode = graph.nodes.find(
                        (n: any) => n.id === edge.to && n.type === "import"
                      );
                      tooltip = `From: ${row.path || row.label}\nTo: ${
                        col.path || col.label
                      }\nImport: ${importNode?.label || "?"}`;
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
