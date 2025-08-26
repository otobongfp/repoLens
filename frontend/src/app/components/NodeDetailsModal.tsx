import React from "react";

interface NodeDetailsModalProps {
  node: any;
  graph: any;
  isOpen: boolean;
  onClose: () => void;
}

export default function NodeDetailsModal({
  node,
  graph,
  isOpen,
  onClose,
}: NodeDetailsModalProps) {
  if (!isOpen || !node || !graph) return null;

  // Get all connections for this node
  const incomingEdges = graph.edges.filter((e: any) => e.to === node.id);
  const outgoingEdges = graph.edges.filter((e: any) => e.from === node.id);

  // Get connected nodes
  const incomingNodes = incomingEdges
    .map((e: any) => graph.nodes.find((n: any) => n.id === e.from))
    .filter(Boolean);

  const outgoingNodes = outgoingEdges
    .map((e: any) => graph.nodes.find((n: any) => n.id === e.to))
    .filter(Boolean);

  // Group connections by type
  const connectionsByType = {
    incoming: incomingEdges.reduce((acc: any, edge: any) => {
      const type = edge.type;
      if (!acc[type]) acc[type] = [];
      acc[type].push(edge);
      return acc;
    }, {}),
    outgoing: outgoingEdges.reduce((acc: any, edge: any) => {
      const type = edge.type;
      if (!acc[type]) acc[type] = [];
      acc[type].push(edge);
      return acc;
    }, {}),
  };

  const getTypeColor = (type: string) => {
    switch (type) {
      case "file":
        return "#1f77b4";
      case "function":
        return "#2ca02c";
      case "class":
        return "#ff7f0e";
      case "import":
        return "#d62728";
      default:
        return "#888";
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case "file":
        return "📄";
      case "function":
        return "⚡";
      case "class":
        return "🏗️";
      case "import":
        return "📦";
      default:
        return "🔗";
    }
  };

  const formatConnectionType = (type: string) => {
    switch (type) {
      case "imports":
        return "Imports";
      case "contains":
        return "Contains";
      case "calls":
        return "Calls";
      default:
        return type.charAt(0).toUpperCase() + type.slice(1);
    }
  };

  const renderNodeInfo = () => {
    return (
      <div className="space-y-4">
        {/* Basic Info */}
        <div className="flex items-center space-x-3">
          <span className="text-2xl">{getTypeIcon(node.type)}</span>
          <div>
            <h3 className="text-xl font-bold text-white">{node.label}</h3>
            <p className="text-gray-400 capitalize">{node.type}</p>
          </div>
        </div>

        {/* File Path */}
        {node.path && node.path !== "external" && (
          <div>
            <h4 className="text-sm font-semibold text-gray-300 mb-1">
              File Path
            </h4>
            <p className="text-sm text-gray-400 font-mono bg-gray-800 p-2 rounded-sm">
              {node.path}
            </p>
          </div>
        )}

        {/* External Function Info */}
        {node.meta?.external && (
          <div className="bg-purple-900/20 border border-purple-500/30 rounded-lg p-3">
            <h4 className="text-sm font-semibold text-purple-300 mb-1">
              External Function
            </h4>
            <p className="text-sm text-purple-200">
              This function is called from external code or libraries
            </p>
          </div>
        )}

        {/* Line Numbers */}
        {node.meta?.start_line && node.meta?.end_line && (
          <div>
            <h4 className="text-sm font-semibold text-gray-300 mb-1">
              Location
            </h4>
            <p className="text-sm text-gray-400">
              Lines {node.meta.start_line} - {node.meta.end_line}
            </p>
          </div>
        )}

        {/* Statistics */}
        <div className="grid grid-cols-2 gap-4">
          <div className="bg-gray-800/50 rounded-lg p-3">
            <h4 className="text-sm font-semibold text-gray-300 mb-1">
              Incoming
            </h4>
            <p className="text-2xl font-bold text-blue-400">
              {incomingEdges.length}
            </p>
            <p className="text-xs text-gray-400">connections</p>
          </div>
          <div className="bg-gray-800/50 rounded-lg p-3">
            <h4 className="text-sm font-semibold text-gray-300 mb-1">
              Outgoing
            </h4>
            <p className="text-2xl font-bold text-green-400">
              {outgoingEdges.length}
            </p>
            <p className="text-xs text-gray-400">connections</p>
          </div>
        </div>
      </div>
    );
  };

  const renderConnections = () => {
    return (
      <div className="space-y-6">
        {/* Incoming Connections */}
        {Object.keys(connectionsByType.incoming).length > 0 && (
          <div>
            <h4 className="text-lg font-semibold text-white mb-3 flex items-center">
              <span className="text-blue-400 mr-2">↓</span>
              Incoming Connections
            </h4>
            {Object.entries(connectionsByType.incoming).map(
              ([type, edges]: [string, any]) => (
                <div key={type} className="mb-4">
                  <h5 className="text-sm font-medium text-gray-300 mb-2">
                    {formatConnectionType(type)} ({edges.length})
                  </h5>
                  <div className="space-y-2">
                    {edges.map((edge: any, index: number) => {
                      const sourceNode = graph.nodes.find(
                        (n: any) => n.id === edge.from
                      );
                      return (
                        <div
                          key={index}
                          className="flex items-center space-x-2 bg-gray-800/30 rounded-sm p-2"
                        >
                          <span
                            className="w-3 h-3 rounded-full"
                            style={{
                              backgroundColor: getTypeColor(
                                sourceNode?.type || "default"
                              ),
                            }}
                          />
                          <span className="text-sm text-gray-300 font-medium">
                            {sourceNode?.label || "Unknown"}
                          </span>
                          <span className="text-xs text-gray-500">
                            ({sourceNode?.type || "unknown"})
                          </span>
                          {edge.meta?.line && (
                            <span className="text-xs text-gray-600 ml-auto">
                              line {edge.meta.line}
                            </span>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )
            )}
          </div>
        )}

        {/* Outgoing Connections */}
        {Object.keys(connectionsByType.outgoing).length > 0 && (
          <div>
            <h4 className="text-lg font-semibold text-white mb-3 flex items-center">
              <span className="text-green-400 mr-2">↑</span>
              Outgoing Connections
            </h4>
            {Object.entries(connectionsByType.outgoing).map(
              ([type, edges]: [string, any]) => (
                <div key={type} className="mb-4">
                  <h5 className="text-sm font-medium text-gray-300 mb-2">
                    {formatConnectionType(type)} ({edges.length})
                  </h5>
                  <div className="space-y-2">
                    {edges.map((edge: any, index: number) => {
                      const targetNode = graph.nodes.find(
                        (n: any) => n.id === edge.to
                      );
                      return (
                        <div
                          key={index}
                          className="flex items-center space-x-2 bg-gray-800/30 rounded-sm p-2"
                        >
                          <span
                            className="w-3 h-3 rounded-full"
                            style={{
                              backgroundColor: getTypeColor(
                                targetNode?.type || "default"
                              ),
                            }}
                          />
                          <span className="text-sm text-gray-300 font-medium">
                            {targetNode?.label || "Unknown"}
                          </span>
                          <span className="text-xs text-gray-500">
                            ({targetNode?.type || "unknown"})
                          </span>
                          {edge.meta?.line && (
                            <span className="text-xs text-gray-600 ml-auto">
                              line {edge.meta.line}
                            </span>
                          )}
                          {edge.meta?.external && (
                            <span className="text-xs text-purple-400 ml-1">
                              external
                            </span>
                          )}
                        </div>
                      );
                    })}
                  </div>
                </div>
              )
            )}
          </div>
        )}

        {/* No Connections */}
        {Object.keys(connectionsByType.incoming).length === 0 &&
          Object.keys(connectionsByType.outgoing).length === 0 && (
            <div className="text-center py-8">
              <p className="text-gray-400">
                No connections found for this node.
              </p>
            </div>
          )}
      </div>
    );
  };

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-gray-900 rounded-lg shadow-2xl max-w-2xl w-full max-h-[90vh] overflow-hidden">
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-700">
          <h2 className="text-xl font-bold text-white">Node Details</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-white transition-colors"
          >
            <svg
              className="w-6 h-6"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Content */}
        <div className="overflow-y-auto max-h-[calc(90vh-80px)]">
          <div className="p-6 space-y-6">
            {renderNodeInfo()}
            {renderConnections()}
          </div>
        </div>
      </div>
    </div>
  );
}
