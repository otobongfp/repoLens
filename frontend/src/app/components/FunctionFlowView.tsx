import React from "react";

export default function FunctionFlowView({ graph }: { graph: any }) {
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

  // Get all functions
  const functions = graph.nodes.filter((n: any) => n.type === "function");

  // For each function, find calls edges
  const callsByFunc: Record<
    string,
    { callee: any; edge: any; isExternal: boolean }[]
  > = {};

  functions.forEach((fn: any) => {
    callsByFunc[fn.id] = [];

    // Find all call edges from this function
    const callEdges = graph.edges.filter(
      (e: any) => e.type === "calls" && e.from === fn.id
    );

    callEdges.forEach((edge: any) => {
      // Try to find the called function as a node
      const callee = graph.nodes.find(
        (n: any) => n.id === edge.to && n.type === "function"
      );

      if (callee) {
        // Internal call - function exists in the graph
        callsByFunc[fn.id].push({ callee, edge, isExternal: false });
      } else {
        // External call - function not found in graph (might be external library or not parsed)
        // Extract function name from the edge.to (format: "func:file:functionName")
        const funcName = edge.to.split(":").pop() || "unknown";
        callsByFunc[fn.id].push({
          callee: {
            id: edge.to,
            label: funcName,
            type: "function",
            path: "external",
            meta: { start_line: "?", end_line: "?" },
          },
          edge,
          isExternal: true,
        });
      }
    });
  });

  const totalCalls = Object.values(callsByFunc).reduce(
    (sum, calls) => sum + calls.length,
    0
  );

  return (
    <div className="py-4">
      <h2 className="text-xl font-bold text-primary mb-4">
        Function Call Flow
      </h2>

      {totalCalls === 0 ? (
        <div className="text-center text-white/70 py-8">
          No function call relationships found. This might be because:
          <ul className="mt-2 text-sm text-white/50 list-disc list-inside">
            <li>Functions don't call other functions</li>
            <li>Call relationships are not being parsed correctly</li>
            <li>All calls are to external libraries</li>
          </ul>
        </div>
      ) : (
        <ul className="space-y-4">
          {functions.map((fn: any) => (
            <li key={fn.id}>
              <div
                className="font-bold text-primary"
                title={`File: ${fn.path || "?"}\nLines: ${
                  fn.meta?.start_line || "?"
                }-${fn.meta?.end_line || "?"}`}
              >
                {fn.label}
                <span className="ml-2 text-sm text-white/60">
                  ({fn.path || "?"})
                </span>
              </div>
              <ul className="pl-4 list-disc text-white/90">
                {callsByFunc[fn.id].length === 0 ? (
                  <li className="text-white/50 italic">No direct calls</li>
                ) : (
                  callsByFunc[fn.id].map(
                    ({ callee, edge, isExternal }: any) => (
                      <li
                        key={callee.id}
                        title={
                          isExternal
                            ? `External call${
                                edge.meta?.line
                                  ? ` at line: ${edge.meta.line}`
                                  : ""
                              }`
                            : `File: ${callee.path || "?"}\nLines: ${
                                callee.meta?.start_line || "?"
                              }-${
                                callee.meta?.end_line || "?"
                              }\nCalled at line: ${edge.meta?.line || "?"}`
                        }
                      >
                        {callee.label}
                        <span className="ml-2 text-xs text-white/60">
                          {isExternal
                            ? "(external)"
                            : `(${callee.path || "?"})`}
                        </span>
                        <span className="ml-2 text-xs text-white/60">
                          (line {edge.meta?.line || "?"})
                        </span>
                      </li>
                    )
                  )
                )}
              </ul>
            </li>
          ))}
        </ul>
      )}

      <div className="mt-4 text-xs text-white/50">
        Shows direct function calls with file paths and line numbers. External
        calls are marked as such.
      </div>
    </div>
  );
}
