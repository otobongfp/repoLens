export async function analyzeRepo(url: string) {
  const res = await fetch("http://localhost:8000/analyze", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ url }),
  });
  if (!res.ok) throw new Error("Failed to analyze repo");
  return await res.json();
}

export async function askRepoQuestion(graph: any, question: string) {
  const res = await fetch("http://localhost:8000/ai/ask", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ graph_data: graph, question }),
  });
  if (!res.ok) throw new Error("Failed to get answer from AI");
  return await res.json();
}
