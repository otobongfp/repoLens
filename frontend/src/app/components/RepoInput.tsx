import { useState } from "react";
import { analyzeRepo } from "../utils/api";

export default function RepoInput({
  setGraph,
  setLoading,
  setError,
}: {
  setGraph: any;
  setLoading: any;
  setError: any;
}) {
  const [url, setUrl] = useState("");

  const handleAnalyze = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setGraph(null);
    try {
      const data = await analyzeRepo(url);
      setGraph(data);
    } catch (err) {
      setError("Failed to analyze repo.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="flex gap-2 w-full max-w-xl mb-6" onSubmit={handleAnalyze}>
      <input
        type="url"
        className="flex-1 border border-gray-300 text-zinc-900 rounded px-4 py-2 focus:outline-none focus:ring-2 focus:ring-[#158452]"
        placeholder="Enter GitHub repo URL (e.g. https://github.com/otobongfp/ledger-guard)"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        required
      />
      <button
        type="submit"
        className="px-5 py-2 bg-primary text-white rounded hover:bg-[#158452] transition"
      >
        Analyze
      </button>
    </form>
  );
}
