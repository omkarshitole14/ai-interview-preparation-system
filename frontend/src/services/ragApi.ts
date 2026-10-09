export type RAGSource = {
  chunk_id: number;
  source: string;
  text: string;
  score: number | null;
};

export type RAGQueryResponse = {
  question: string;
  answer: string;
  mode: "rag" | "general";
  source_label: string;
  sources: RAGSource[];
};

const API_URL = process.env.NEXT_PUBLIC_API_URL;

if (!API_URL) {
  throw new Error("NEXT_PUBLIC_API_URL is not configured.");
}

export async function queryRAG(
  question: string,
  topK: number = 3,
): Promise<RAGQueryResponse> {
  const response = await fetch(`${API_URL}/api/rag/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question,
      top_k: topK,
    }),
  });

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    if (response.status === 503) {
      throw new Error(
        "The AI service is temporarily unavailable because the Gemini API quota has been exceeded. Please try again later.",
      );
    }

    throw new Error(
      data?.detail || "RAG query failed.",
    );
  }

  return data as RAGQueryResponse;
}