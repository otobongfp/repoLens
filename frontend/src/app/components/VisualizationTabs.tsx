import { useState } from "react";
import GraphView from "./GraphView";
import TreeView from "./TreeView";
import DependencyMatrixView from "./DependencyMatrixView";
import FunctionFlowView from "./FunctionFlowView";
import HeatmapView from "./HeatmapView";

const TABS = [
  { key: "graph", label: "Graph View" },
  { key: "tree", label: "Tree View" },
  { key: "matrix", label: "Dependency Matrix" },
  { key: "flow", label: "Function Flow" },
  { key: "heatmap", label: "Heatmap" },
];

export default function VisualizationTabs({ graph }: { graph: any }) {
  const [active, setActive] = useState("graph");

  return (
    <div className="w-full">
      <div className="flex gap-2 mb-4 border-b border-white/10">
        {TABS.map((tab) => (
          <button
            key={tab.key}
            className={`px-4 py-2 font-semibold rounded-t transition focus:outline-none
              ${
                active === tab.key
                  ? "border-b-4 border-primary text-primary bg-white/5"
                  : "text-white/80 hover:bg-white/10"
              }`}
            onClick={() => setActive(tab.key)}
            aria-selected={active === tab.key}
            tabIndex={0}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div className="transition-opacity duration-300">
        {active === "graph" && <GraphView graph={graph} />}
        {active === "tree" && <TreeView graph={graph} />}
        {active === "matrix" && <DependencyMatrixView graph={graph} />}
        {active === "flow" && <FunctionFlowView graph={graph} />}
        {active === "heatmap" && <HeatmapView graph={graph} />}
      </div>
    </div>
  );
}
