import React from "react";
import { useGraphData } from "../context/GraphDataProvider";

function renderTree(graph: any) {
  // Group nodes by file
  const files = graph.nodes.filter((n: any) => n.type === "file");
  const childrenByFile: Record<string, any[]> = {};
  files.forEach((file: any) => {
    childrenByFile[file.id] = graph.nodes.filter(
      (n: any) =>
        (n.type === "function" || n.type === "class") &&
        graph.edges.some(
          (e: any) =>
            e.from === file.id && e.to === n.id && e.type === "contains"
        )
    );
  });
  return (
    <ul className="pl-4">
      {files.map((file: any) => (
        <li key={file.id} className="mb-2">
          <span className="font-bold text-primary">{file.label}</span>
          <ul className="pl-4">
            {childrenByFile[file.id].map((child) => (
              <li key={child.id} className="text-white/90">
                {child.label}{" "}
                <span className="text-xs text-white/50">({child.type})</span>
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
      <div className="text-center text-lg text-primary py-16">No data</div>
    );
  return (
    <div className="py-4">
      <h2 className="text-xl font-bold text-primary mb-4">
        Code Structure Tree
      </h2>
      {renderTree(graph)}
    </div>
  );
}
