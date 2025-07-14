import { useEffect, useRef, useState } from "react";
import * as d3 from "d3";
import NodeDetailsModal from "./NodeDetailsModal";

export default function GraphView({
  graph,
  fullscreen,
  setFullscreen,
}: {
  graph: any;
  fullscreen?: boolean;
  setFullscreen?: (v: boolean) => void;
}) {
  const svgRef = useRef<SVGSVGElement | null>(null);
  const [browserFullscreen, setBrowserFullscreen] = useState(false);
  const [selectedNode, setSelectedNode] = useState<any>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // Browser fullscreen functions
  const enterBrowserFullscreen = () => {
    if (svgRef.current) {
      if (svgRef.current.requestFullscreen) {
        svgRef.current.requestFullscreen();
      } else if ((svgRef.current as any).webkitRequestFullscreen) {
        (svgRef.current as any).webkitRequestFullscreen();
      } else if ((svgRef.current as any).msRequestFullscreen) {
        (svgRef.current as any).msRequestFullscreen();
      }
    }
  };

  const exitBrowserFullscreen = () => {
    if (document.exitFullscreen) {
      document.exitFullscreen();
    } else if ((document as any).webkitExitFullscreen) {
      (document as any).webkitExitFullscreen();
    } else if ((document as any).msExitFullscreen) {
      (document as any).msExitFullscreen();
    }
  };

  // Listen for fullscreen changes
  useEffect(() => {
    const handleFullscreenChange = () => {
      setBrowserFullscreen(!!document.fullscreenElement);
    };

    document.addEventListener("fullscreenchange", handleFullscreenChange);
    document.addEventListener("webkitfullscreenchange", handleFullscreenChange);
    document.addEventListener("msfullscreenchange", handleFullscreenChange);

    return () => {
      document.removeEventListener("fullscreenchange", handleFullscreenChange);
      document.removeEventListener(
        "webkitfullscreenchange",
        handleFullscreenChange
      );
      document.removeEventListener(
        "msfullscreenchange",
        handleFullscreenChange
      );
    };
  }, []);

  useEffect(() => {
    if (!graph || !Array.isArray(graph.nodes) || !Array.isArray(graph.edges)) {
      return;
    }

    const svg = d3.select(svgRef.current);
    svg.selectAll("*").remove();

    // Use full browser dimensions when in browser fullscreen
    const width = browserFullscreen ? window.innerWidth : 800;
    const height = browserFullscreen ? window.innerHeight : 600;

    svg.attr("width", width).attr("height", height);

    const nodes = graph.nodes.map((n: any) => ({ ...n }));

    // Create a set of valid node IDs for quick lookup
    const validNodeIds = new Set(nodes.map((n: any) => n.id));

    // Filter edges to only include those where both source and target nodes exist
    const links = graph.edges
      .filter((e: any) => {
        const hasSource = validNodeIds.has(e.from);
        const hasTarget = validNodeIds.has(e.to);
        if (!hasSource || !hasTarget) {
          console.warn(
            `Skipping edge ${e.from} -> ${e.to}: ${
              !hasSource ? "source missing" : "target missing"
            }`
          );
        }
        return hasSource && hasTarget;
      })
      .map((e: any) => ({
        source: e.from,
        target: e.to,
        type: e.type,
        meta: e.meta,
      }));

    const simulation = d3
      .forceSimulation(nodes)
      .force(
        "link",
        d3
          .forceLink(links)
          .id((d: any) => d.id)
          .distance(100)
      )
      .force("charge", d3.forceManyBody().strength(-300))
      .force("center", d3.forceCenter(width / 2, height / 2));

    const link = svg
      .append("g")
      .attr("stroke", "#999")
      .attr("stroke-opacity", 0.6)
      .selectAll("line")
      .data(links)
      .join("line")
      .attr("stroke-width", 1.5)
      .append("title")
      .text((d: any) => {
        let label = `${d.type}`;
        if (d.meta && d.meta.line) label += ` (line ${d.meta.line})`;
        return label;
      });

    const node = (
      svg
        .append("g")
        .attr("stroke", "#fff")
        .attr("stroke-width", 1.5)
        .selectAll("g")
        .data(nodes)
        .join("g") as any
    )
      .call(drag(simulation))
      .style("cursor", "pointer")
      .on("click", (event: any, d: any) => {
        setSelectedNode(d);
        setIsModalOpen(true);
      })
      .on("mouseover", function (this: any, event: any, d: any) {
        d3.select(this)
          .select("circle")
          .transition()
          .duration(200)
          .attr("r", browserFullscreen ? 16 : 12);
        d3.select(this)
          .select("text")
          .transition()
          .duration(200)
          .style("font-weight", "bold");
      })
      .on("mouseout", function (this: any, event: any, d: any) {
        d3.select(this)
          .select("circle")
          .transition()
          .duration(200)
          .attr("r", browserFullscreen ? 12 : 8);
        d3.select(this)
          .select("text")
          .transition()
          .duration(200)
          .style("font-weight", "normal");
      });

    node
      .append("circle")
      .attr("r", browserFullscreen ? 12 : 8)
      .attr("fill", (d: any) => colorForType(d.type, d.meta))
      .style("filter", "drop-shadow(0 0 4px rgba(255,255,255,0.1))");

    node.append("title").text((d: any) => {
      if (d.type === "file") {
        return `${d.label} (file)\nPath: ${d.path}`;
      } else if (d.type === "function") {
        if (d.meta?.external) {
          return `${d.label} (external function)\nCalled from: ${
            d.meta?.parent_file || "unknown"
          }`;
        } else {
          return `${d.label} (function)\nFile: ${d.path}\nLines: ${d.meta?.start_line}-${d.meta?.end_line}`;
        }
      } else if (d.type === "class") {
        return `${d.label} (class)\nFile: ${d.path}\nLines: ${d.meta?.start_line}-${d.meta?.end_line}`;
      } else if (d.type === "import") {
        return `${d.label} (import)\nSource: ${d.meta?.source_file}`;
      }
      return `${d.label} (${d.type})`;
    });

    node
      .append("text")
      .text((d: any) => d.label)
      .attr("x", browserFullscreen ? 16 : 12)
      .attr("y", "0.31em")
      .attr("fill", "#1db470")
      .style("font-size", browserFullscreen ? "14px" : "10px");

    simulation.on("tick", () => {
      svg
        .selectAll("line")
        .attr("x1", (d: any) => d.source.x)
        .attr("y1", (d: any) => d.source.y)
        .attr("x2", (d: any) => d.target.x)
        .attr("y2", (d: any) => d.target.y);
      node.attr("transform", (d: any) => `translate(${d.x},${d.y})`);
    });

    function colorForType(type: string, meta?: any) {
      switch (type) {
        case "file":
          return "#1f77b4";
        case "function":
          return meta?.external ? "#9467bd" : "#2ca02c"; // Purple for external functions
        case "class":
          return "#ff7f0e";
        case "import":
          return "#d62728";
        default:
          return "#888";
      }
    }

    function drag(simulation: any) {
      function dragstarted(event: any, d: any) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
      }
      function dragged(event: any, d: any) {
        d.fx = event.x;
        d.fy = event.y;
      }
      function dragended(event: any, d: any) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
      }
      return d3
        .drag()
        .on("start", dragstarted)
        .on("drag", dragged)
        .on("end", dragended);
    }
  }, [graph, browserFullscreen]);

  return (
    <div
      className={`relative w-full flex justify-center items-center ${
        fullscreen ? "h-full" : ""
      }`}
    >
      {/* Container fullscreen button */}
      {setFullscreen && (
        <button
          className="absolute top-4 right-4 z-10 bg-primary text-white rounded-full p-2 shadow-lg hover:bg-primary/80 transition"
          onClick={() => setFullscreen(!fullscreen)}
          title="Toggle container fullscreen"
        >
          {fullscreen ? "Exit Fullscreen" : "Fullscreen"}
        </button>
      )}

      {/* Browser fullscreen button */}
      <button
        className="absolute top-4 right-16 z-10 bg-primary text-white rounded-full p-2 shadow-lg hover:bg-[#158452] transition"
        onClick={
          browserFullscreen ? exitBrowserFullscreen : enterBrowserFullscreen
        }
        title={
          browserFullscreen
            ? "Exit browser fullscreen"
            : "Enter browser fullscreen"
        }
      >
        {browserFullscreen ? "Exit Fullscreen" : "Fullscreen"}
      </button>

      <svg
        ref={svgRef}
        className={`border rounded bg-white/5 shadow ${
          fullscreen ? "w-full h-[90vh]" : ""
        } ${browserFullscreen ? "w-full h-full" : ""}`}
      />

      {/* Help text */}
      <div className="absolute bottom-4 left-4 text-xs text-gray-400 bg-black/50 px-2 py-1 rounded">
        💡 Click any node to see details
      </div>

      {/* Node Details Modal */}
      <NodeDetailsModal
        node={selectedNode}
        graph={graph}
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedNode(null);
        }}
      />
    </div>
  );
}
