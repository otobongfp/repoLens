import React, { useEffect, useRef, useState } from "react";
import * as d3 from "d3";

interface HeatmapData {
  id: string;
  label: string;
  path?: string;
  type: string;
  heat: number;
  functions?: number;
  imports?: number;
  calls?: number;
  centrality?: number;
}

import { useGraphData } from "../context/GraphDataProvider";

export default function HeatmapView() {
  const { graph } = useGraphData();
  const svgRef = useRef<SVGSVGElement>(null);
  const [selectedNode, setSelectedNode] = useState<HeatmapData | null>(null);

  useEffect(() => {
    if (!graph || !svgRef.current) return;

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    const width = 800;
    const height = 600;
    const margin = { top: 20, right: 20, bottom: 20, left: 20 };

    // Calculate heatmap data for each node
    const heatmapData: HeatmapData[] = graph.nodes.map((node: any) => {
      // Count connections (in-degree + out-degree)
      const inEdges = graph.edges.filter((e: any) => e.to === node.id);
      const outEdges = graph.edges.filter((e: any) => e.from === node.id);
      const totalConnections = inEdges.length + outEdges.length;

      // Count functions in this file (if it's a file node)
      const functionsInFile =
        node.type === "file"
          ? graph.nodes.filter(
              (n: any) =>
                n.type === "function" &&
                graph.edges.some(
                  (e: any) =>
                    e.type === "contains" && e.from === node.id && e.to === n.id
                )
            ).length
          : 0;

      // Count local imports in this file
      const localImportsInFile =
        node.type === "file"
          ? graph.edges.filter(
              (e: any) =>
                e.type === "imports" &&
                e.from === node.id &&
                e.meta?.local === true
            ).length
          : 0;

      // Count function calls (if it's a function node)
      const functionCalls =
        node.type === "function"
          ? graph.edges.filter(
              (e: any) => e.type === "calls" && e.from === node.id
            ).length
          : 0;

      // Calculate centrality (how central this node is in the network)
      const centrality = totalConnections / Math.max(graph.nodes.length - 1, 1);

      // Calculate heat score based on node type
      let heat = 0;
      if (node.type === "file") {
        heat =
          functionsInFile * 2 + localImportsInFile * 1.5 + totalConnections * 3;
      } else if (node.type === "function") {
        heat = functionCalls * 4 + totalConnections * 2;
      } else if (node.type === "module") {
        heat = totalConnections * 1.5;
      } else {
        heat = totalConnections * 2;
      }

      return {
        id: node.id,
        label: node.label,
        path: node.path,
        type: node.type,
        heat,
        functions: functionsInFile,
        imports: localImportsInFile,
        calls: functionCalls,
        centrality,
      };
    });

    // Filter out nodes with zero heat for cleaner visualization
    const activeData = heatmapData.filter((d: HeatmapData) => d.heat > 0);

    if (activeData.length === 0) {
      svg
        .append("text")
        .attr("x", width / 2)
        .attr("y", height / 2)
        .attr("text-anchor", "middle")
        .attr("fill", "#888")
        .text("No data to visualize");
      return;
    }

    // Sort by heat for better visualization
    activeData.sort((a: HeatmapData, b: HeatmapData) => b.heat - a.heat);

    // Create scales
    const xScale = d3
      .scaleBand()
      .domain(activeData.map((d: HeatmapData) => d.id))
      .range([margin.left, width - margin.right])
      .padding(0.1);

    const yScale = d3
      .scaleLinear()
      .domain([0, d3.max(activeData, (d: HeatmapData) => d.heat) || 0])
      .range([height - margin.bottom, margin.top]);

    const colorScale = d3
      .scaleSequential()
      .domain([0, d3.max(activeData, (d: HeatmapData) => d.heat) || 0])
      .interpolator(d3.interpolateReds);

    // Create bars
    svg
      .selectAll("rect")
      .data(activeData)
      .enter()
      .append("rect")
      .attr("x", (d) => xScale(d.id) || 0)
      .attr("y", (d) => yScale(d.heat))
      .attr("width", xScale.bandwidth())
      .attr("height", (d) => height - margin.bottom - yScale(d.heat))
      .attr("fill", (d) => colorScale(d.heat))
      .attr("stroke", "#333")
      .attr("stroke-width", 1)
      .style("cursor", "pointer")
      .on("click", function (event, d) {
        setSelectedNode(d);
      })
      .on("mouseover", function (event, d) {
        d3.select(this).attr("stroke", "#fff").attr("stroke-width", 2);

        // Show tooltip
        const tooltip = svg
          .append("g")
          .attr("class", "tooltip")
          .attr(
            "transform",
            `translate(${event.pageX + 10}, ${event.pageY - 10})`
          );

        tooltip
          .append("rect")
          .attr("width", 200)
          .attr("height", 80)
          .attr("fill", "rgba(0,0,0,0.8)")
          .attr("rx", 5);

        tooltip
          .append("text")
          .attr("x", 10)
          .attr("y", 20)
          .attr("fill", "white")
          .style("font-size", "12px")
          .text(`${d.label} (${d.type})`);

        tooltip
          .append("text")
          .attr("x", 10)
          .attr("y", 35)
          .attr("fill", "white")
          .style("font-size", "10px")
          .text(`Heat: ${d.heat.toFixed(1)}`);

        if (d.functions !== undefined) {
          tooltip
            .append("text")
            .attr("x", 10)
            .attr("y", 50)
            .attr("fill", "white")
            .style("font-size", "10px")
            .text(`Functions: ${d.functions}`);
        }

        if (d.imports !== undefined) {
          tooltip
            .append("text")
            .attr("x", 10)
            .attr("y", 65)
            .attr("fill", "white")
            .style("font-size", "10px")
            .text(`Local Imports: ${d.imports}`);
        }
      })
      .on("mouseout", function () {
        d3.select(this).attr("stroke", "#333").attr("stroke-width", 1);
        svg.selectAll(".tooltip").remove();
      });

    // Add axis
    const yAxis = d3.axisLeft(yScale);
    svg
      .append("g")
      .attr("transform", `translate(${margin.left}, 0)`)
      .call(yAxis);

    // Remove x-axis labels to avoid congestion
    const xAxis = d3.axisBottom(xScale).tickFormat(() => "");
    svg
      .append("g")
      .attr("transform", `translate(0, ${height - margin.bottom})`)
      .call(xAxis);
  }, [graph]);

  return (
    <div className="py-4">
      <h2 className="text-xl font-bold text-primary mb-4">Code Heatmap</h2>

      {/* Selected node info */}
      {selectedNode && (
        <div className="mb-4 p-3 bg-white/5 rounded-sm border border-white/10">
          <div className="flex items-center gap-2 mb-2">
            <span className="text-primary font-bold">📊</span>
            <span className="font-semibold text-primary">
              {selectedNode.label}
            </span>
            <span className="text-white/60 text-sm">({selectedNode.type})</span>
          </div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-white/70">Heat Score:</span>
              <span className="ml-2 text-primary font-bold">
                {selectedNode.heat.toFixed(1)}
              </span>
            </div>
            {selectedNode.functions !== undefined && (
              <div>
                <span className="text-white/70">Functions:</span>
                <span className="ml-2 text-green-400">
                  {selectedNode.functions}
                </span>
              </div>
            )}
            {selectedNode.imports !== undefined && (
              <div>
                <span className="text-white/70">Local Imports:</span>
                <span className="ml-2 text-blue-400">
                  {selectedNode.imports}
                </span>
              </div>
            )}
            {selectedNode.calls !== undefined && (
              <div>
                <span className="text-white/70">Function Calls:</span>
                <span className="ml-2 text-yellow-400">
                  {selectedNode.calls}
                </span>
              </div>
            )}
            {selectedNode.path && (
              <div className="col-span-2">
                <span className="text-white/70">Path:</span>
                <span className="ml-2 text-white/90 font-mono text-xs">
                  {selectedNode.path}
                </span>
              </div>
            )}
          </div>
          <button
            onClick={() => setSelectedNode(null)}
            className="mt-2 text-xs text-white/50 hover:text-white/70"
          >
            Clear selection
          </button>
        </div>
      )}

      <div className="overflow-auto">
        <svg
          ref={svgRef}
          width="800"
          height="600"
          className="bg-background border border-white/10 rounded-sm"
        />
      </div>
      <div className="mt-4 text-xs text-white/50">
        Click on bars to see file details. Redder = higher complexity/activity.
      </div>
    </div>
  );
}
