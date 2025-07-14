import React, { useState } from "react";
import VisualizationTabs from "./VisualizationTabs";
import AIAnalysisView from "./AIAnalysisView";

interface MainTabsProps {
  graph: any;
}

export default function MainTabs({ graph }: MainTabsProps) {
  const [activeMode, setActiveMode] = useState<"visualization" | "ai-analysis">(
    "visualization"
  );

  return (
    <div className="w-full">
      {/* Main Mode Tabs */}
      <div className="flex gap-2 mb-6 border-b border-white/10">
        <button
          className={`px-6 py-3 font-semibold rounded-t transition focus:outline-none
            ${
              activeMode === "visualization"
                ? "border-b-4 border-primary text-primary bg-white/5"
                : "text-white/80 hover:bg-white/10"
            }`}
          onClick={() => setActiveMode("visualization")}
        >
          📊 Visualization
        </button>
        <button
          className={`px-6 py-3 font-semibold rounded-t transition focus:outline-none
            ${
              activeMode === "ai-analysis"
                ? "border-b-4 border-primary text-primary bg-white/5"
                : "text-white/80 hover:bg-white/10"
            }`}
          onClick={() => setActiveMode("ai-analysis")}
        >
          🤖 AI Analysis
        </button>
      </div>

      {/* Content */}
      <div className="transition-opacity duration-300">
        {activeMode === "visualization" && <VisualizationTabs graph={graph} />}
        {activeMode === "ai-analysis" && <AIAnalysisView graph={graph} />}
      </div>
    </div>
  );
}
