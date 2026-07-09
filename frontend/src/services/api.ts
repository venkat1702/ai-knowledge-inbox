// src/services/api.ts

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

type IngestRequest =
  | {
      source_type: "text";
      content: string;
      title?: string;
    }
  | {
      source_type: "url";
      url: string;
      title?: string;
    };

export async function getItems() {
  const response = await fetch(`${API_BASE_URL}/items`);
  return response.json();
}

export async function ingest(data: IngestRequest) {
  const response = await fetch(`${API_BASE_URL}/ingest`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });

  if (!response.ok) {
    throw new Error("Failed to ingest content");
  }

  return response.json();
}

export async function query(question: string, top_k = 5) {
  const response = await fetch(`${API_BASE_URL}/query`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      question,
      top_k,
    }),
  });

  if (!response.ok) {
    throw new Error("Failed to query");
  }

  return response.json();
}
