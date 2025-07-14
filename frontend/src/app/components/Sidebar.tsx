import { useState } from "react";

export default function Sidebar({ graph }: { graph: any }) {
  const [question, setQuestion] = useState("");
  const [history, setHistory] = useState<{ q: string; a: string }[]>([]);

  const handleAsk = (e: React.FormEvent) => {
    e.preventDefault();
    if (!question.trim()) return;
    // TODO: Call LLM backend with { graph, question }
    setHistory(
      [{ q: question, a: "AI answer (stub)" }, ...history].slice(0, 5)
    );
    setQuestion("");
  };

  return (
    <aside className="h-full w-80 min-w-[18rem] bg-sidebar border-r border-white/10 p-4 flex flex-col transition-all duration-300 shadow-xl">
      <h2 className="font-bold text-lg mb-2 text-primary">Ask RepoLens AI</h2>
      <form onSubmit={handleAsk} className="flex flex-col gap-2 mb-4">
        <textarea
          className="border border-white/10 bg-background text-white rounded p-2 resize-none h-20 focus:outline-none focus:ring-2 focus:ring-primary"
          placeholder="Ask about the codebase..."
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
        <button
          type="submit"
          className="bg-primary text-white rounded px-4 py-2 hover:bg-primary/80 transition font-semibold"
        >
          Ask
        </button>
      </form>
      <div className="flex-1 overflow-auto">
        <h3 className="font-semibold mb-1 text-white">Recent Questions</h3>
        <ul className="space-y-2">
          {history.map((item, i) => (
            <li
              key={i}
              className="bg-background/80 rounded p-2 shadow text-sm border border-white/5"
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
