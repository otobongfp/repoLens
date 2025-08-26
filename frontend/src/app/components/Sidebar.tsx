import { useState } from "react";
import { useRepolensApi } from "../utils/api";
import { useGraphData } from "../context/GraphDataProvider";

export default function Sidebar() {
  const { graph } = useGraphData();
  const { askRepoQuestion } = useRepolensApi();
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState<{ q: string; a: string }[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleAsk = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;
    if (!graph || !graph.nodes || !graph.edges) {
      setError("Please analyze a repository first before asking questions.");
      return;
    }

    // Check if graph is very large
    const nodeCount = graph.nodes?.length || 0;
    const edgeCount = graph.edges?.length || 0;

    if (nodeCount > 1000 || edgeCount > 2000) {
      setError(
        "Graph is very large. The AI will use a simplified analysis to avoid token limits."
      );
    }

    setLoading(true);
    setError(null);
    try {
      const data = await askRepoQuestion(graph, question);
      setHistory(
        [
          { q: question, a: data.answer || "No answer from AI." },
          ...history,
        ].slice(0, 5)
      );
    } catch (err) {
      setError("Failed to get answer from AI.");
    } finally {
      setLoading(false);
      setQuestion("");
    }
  };

  return (
    <aside className="h-full w-80 min-w-[18rem] bg-sidebar border-r border-white/10 p-4 flex flex-col transition-all duration-300 shadow-xl">
      <h2 className="font-bold text-lg mb-2 text-primary">Ask RepoLens AI</h2>
      <p className="text-xs text-gray-400 mb-3">
        Ask about classes, functions, code structure, and implementation details
      </p>
      <form onSubmit={handleAsk} className="flex flex-col gap-2 mb-4">
        <textarea
          className="border border-white/10 bg-background text-black rounded-sm p-2 resize-none h-20 focus:outline-hidden focus:ring-2 focus:ring-primary"
          placeholder={
            !graph || !graph.nodes
              ? "Please analyze a repository first..."
              : "Ask about the codebase..."
          }
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          disabled={loading || !graph || !graph.nodes}
        />
        <button
          type="submit"
          className="bg-primary text-white rounded-sm px-4 py-2 hover:bg-primary/80 transition font-semibold disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={loading || !graph || !graph.nodes}
        >
          {loading ? "Asking..." : "Ask"}
        </button>
      </form>
      {error && <div className="text-red-400 mb-2">{error}</div>}
      <div className="flex-1 overflow-auto">
        <h3 className="font-semibold mb-1 text-white">Recent Questions</h3>
        <ul className="space-y-2">
          {history.map((item, i) => (
            <li
              key={i}
              className="bg-background/80 rounded-sm p-2 shadow-sm text-sm border border-white/5"
            >
              <div className="font-medium text-primary">Q: {item.q}</div>
              <div className="text-white/80">A: {item.a}</div>
            </li>
          ))}
        </ul>
      </div>
    </aside>
  );
}
