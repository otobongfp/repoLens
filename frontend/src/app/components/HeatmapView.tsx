import React, { useEffect, useRef } from "react";
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

export default function HeatmapView({ graph }: { graph: any }) {
  const svgRef = useRef<SVGSVGElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  // Guard against invalid graph structure
  if (!graph || !Array.isArray(graph.nodes) || !Array.isArray(graph.edges)) {
    return (
      <div className="text-center text-lg text-primary py-16">
        Invalid graph data
      </div>
    );
  }

  useEffect(() => {
    if (!svgRef.current || !containerRef.current || !graph) return;

    // Clear previous content
    d3.select(svgRef.current).selectAll("*").remove();

    // Remove any existing tooltips
    d3.selectAll(".tooltip").remove();

    // Calculate heat values for each node
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
                n.type === "function" && n.meta?.source_file === node.path
            ).length
          : 0;

      // Count imports in this file
      const importsInFile =
        node.type === "file"
          ? graph.nodes.filter(
              (n: any) =>
                n.type === "import" && n.meta?.source_file === node.path
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
        heat = functionsInFile * 2 + importsInFile * 1.5 + totalConnections * 3;
      } else if (node.type === "function") {
        heat = functionCalls * 4 + totalConnections * 2;
      } else if (node.type === "import") {
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
        imports: importsInFile,
        calls: functionCalls,
        centrality,
      };
    });

    // Filter out nodes with zero heat for cleaner visualization
    const activeData = heatmapData.filter((d) => d.heat > 0);

    if (activeData.length === 0) {
      return;
    }

    // Sort by heat value (descending)
    activeData.sort((a, b) => b.heat - a.heat);

    // Setup dimensions
    const container = containerRef.current;
    const width = container.clientWidth;
    const height = Math.max(400, activeData.length * 30 + 100);

    // Setup SVG
    const svg = d3
      .select(svgRef.current)
      .attr("width", width)
      .attr("height", height);

    // Create color scale
    const maxHeat = d3.max(activeData, (d) => d.heat) || 1;
    const colorScale = d3
      .scaleSequential()
      .domain([0, maxHeat])
      .interpolator(d3.interpolateRgb("#1e293b", "#f59e0b")); // slate-800 to amber-500

    // Create scales
    const xScale = d3
      .scaleBand()
      .domain(["heat", "functions", "imports", "calls", "centrality"])
      .range([100, width - 20])
      .padding(0.1);

    const yScale = d3
      .scaleBand()
      .domain(activeData.map((d) => d.id))
      .range([60, height - 40])
      .padding(0.1);

    // Add background
    svg
      .append("rect")
      .attr("width", width)
      .attr("height", height)
      .attr("fill", "#0f172a"); // slate-900

    // Add title
    svg
      .append("text")
      .attr("x", width / 2)
      .attr("y", 25)
      .attr("text-anchor", "middle")
      .attr("fill", "#f59e0b")
      .attr("font-size", "18px")
      .attr("font-weight", "bold")
      .text("Code Usage Heatmap");

    // Add column headers
    const columnHeaders = [
      { key: "heat", label: "Heat Score" },
      { key: "functions", label: "Functions" },
      { key: "imports", label: "Imports" },
      { key: "calls", label: "Calls" },
      { key: "centrality", label: "Centrality" },
    ];

    columnHeaders.forEach((col, i) => {
      svg
        .append("text")
        .attr("x", xScale(col.key)! + xScale.bandwidth() / 2)
        .attr("y", 50)
        .attr("text-anchor", "middle")
        .attr("fill", "#e2e8f0")
        .attr("font-size", "12px")
        .attr("font-weight", "bold")
        .text(col.label);
    });

    // Create heatmap cells
    activeData.forEach((d, i) => {
      const y = yScale(d.id)!;

      // Add row label (node name)
      svg
        .append("text")
        .attr("x", 95)
        .attr("y", y + yScale.bandwidth() / 2 + 4)
        .attr("text-anchor", "end")
        .attr("fill", "#e2e8f0")
        .attr("font-size", "11px")
        .attr("font-family", "monospace")
        .text(d.label.length > 20 ? d.label.substring(0, 17) + "..." : d.label);

      // Add type indicator
      svg
        .append("text")
        .attr("x", 5)
        .attr("y", y + yScale.bandwidth() / 2 + 4)
        .attr("text-anchor", "start")
        .attr("fill", getTypeColor(d.type))
        .attr("font-size", "10px")
        .attr("font-weight", "bold")
        .text(d.type.charAt(0).toUpperCase());

      // Create cells for each metric
      const metrics = [
        { key: "heat", value: d.heat, color: colorScale(d.heat) },
        {
          key: "functions",
          value: d.functions || 0,
          color: d.functions ? "#10b981" : "#374151",
        },
        {
          key: "imports",
          value: d.imports || 0,
          color: d.imports ? "#3b82f6" : "#374151",
        },
        {
          key: "calls",
          value: d.calls || 0,
          color: d.calls ? "#f59e0b" : "#374151",
        },
        {
          key: "centrality",
          value: d.centrality || 0,
          color: d.centrality ? "#8b5cf6" : "#374151",
        },
      ];

      metrics.forEach((metric) => {
        const x = xScale(metric.key)!;
        const cellWidth = xScale.bandwidth();
        const cellHeight = yScale.bandwidth();

        // Add cell background with tooltip functionality
        const rect = svg
          .append("rect")
          .attr("x", x)
          .attr("y", y)
          .attr("width", cellWidth)
          .attr("height", cellHeight)
          .attr("fill", metric.color)
          .attr("stroke", "#374151")
          .attr("stroke-width", 1)
          .attr("rx", 2)
          .style("cursor", "pointer");

        // Add value text
        svg
          .append("text")
          .attr("x", x + cellWidth / 2)
          .attr("y", y + cellHeight / 2 + 4)
          .attr("text-anchor", "middle")
          .attr("fill", getTextColor(metric.color))
          .attr("font-size", "11px")
          .attr("font-weight", "bold")
          .text(metric.value.toFixed(1));

        // Add tooltip
        const tooltip = d3
          .select("body")
          .append("div")
          .attr("class", "tooltip")
          .style("position", "absolute")
          .style("background", "#1e293b")
          .style("color", "#e2e8f0")
          .style("padding", "8px")
          .style("border-radius", "4px")
          .style("font-size", "12px")
          .style("pointer-events", "none")
          .style("opacity", 0)
          .style("z-index", 1000)
          .style("border", "1px solid #374151");

        rect
          .on("mouseover", function (event) {
            const tooltipContent = `
              <strong>${d.label}</strong><br/>
              Type: ${d.type}<br/>
              ${metric.key}: ${metric.value.toFixed(2)}<br/>
              ${d.path ? `Path: ${d.path}` : ""}
            `;
            tooltip.html(tooltipContent).style("opacity", 1);
          })
          .on("mousemove", function (event) {
            tooltip
              .style("left", event.pageX + 10 + "px")
              .style("top", event.pageY - 10 + "px");
          })
          .on("mouseout", function () {
            tooltip.style("opacity", 0);
          });
      });
    });

    // Add legend
    const legend = svg
      .append("g")
      .attr("transform", `translate(20, ${height - 80})`);

    legend
      .append("text")
      .attr("x", 0)
      .attr("y", -10)
      .attr("fill", "#e2e8f0")
      .attr("font-size", "12px")
      .attr("font-weight", "bold")
      .text("Legend:");

    const legendItems = [
      { color: "#f59e0b", label: "Heat Score" },
      { color: "#10b981", label: "Functions" },
      { color: "#3b82f6", label: "Imports" },
      { color: "#f59e0b", label: "Calls" },
      { color: "#8b5cf6", label: "Centrality" },
    ];

    legendItems.forEach((item, i) => {
      const x = i * 120;
      legend
        .append("rect")
        .attr("x", x)
        .attr("y", 0)
        .attr("width", 12)
        .attr("height", 12)
        .attr("fill", item.color)
        .attr("rx", 2);

      legend
        .append("text")
        .attr("x", x + 18)
        .attr("y", 10)
        .attr("fill", "#e2e8f0")
        .attr("font-size", "11px")
        .text(item.label);
    });

    // Add type legend
    const typeLegend = svg
      .append("g")
      .attr("transform", `translate(20, ${height - 40})`);

    typeLegend
      .append("text")
      .attr("x", 0)
      .attr("y", -10)
      .attr("fill", "#e2e8f0")
      .attr("font-size", "12px")
      .attr("font-weight", "bold")
      .text("Types:");

    const types = [
      { color: "#10b981", label: "File" },
      { color: "#3b82f6", label: "Function" },
      { color: "#f59e0b", label: "Import" },
    ];

    types.forEach((type, i) => {
      const x = i * 80;
      typeLegend
        .append("circle")
        .attr("cx", x + 6)
        .attr("cy", 0)
        .attr("r", 4)
        .attr("fill", type.color);

      typeLegend
        .append("text")
        .attr("x", x + 16)
        .attr("y", 4)
        .attr("fill", "#e2e8f0")
        .attr("font-size", "11px")
        .text(type.label);
    });
  }, [graph]);

  function getTypeColor(type: string): string {
    switch (type) {
      case "file":
        return "#10b981"; // emerald-500
      case "function":
        return "#3b82f6"; // blue-500
      case "import":
        return "#f59e0b"; // amber-500
      default:
        return "#6b7280"; // gray-500
    }
  }

  function getTextColor(bgColor: string): string {
    // Simple logic to determine text color based on background
    if (bgColor === "#374151") return "#9ca3af"; // gray-400 for dark backgrounds
    return "#ffffff"; // white for colored backgrounds
  }

  return (
    <div className="py-4">
      <h2 className="text-xl font-bold text-primary mb-4">
        Code Usage Heatmap
      </h2>
      <div ref={containerRef} className="w-full overflow-auto">
        <svg ref={svgRef} className="w-full"></svg>
      </div>
      <div className="mt-4 text-xs text-white/50">
        Heatmap shows code usage intensity. Higher values indicate more
        activity, connections, or complexity. Hover over cells for detailed
        information.
      </div>
    </div>
  );
}
