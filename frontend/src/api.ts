import type { CartResponse, ChatResponse, ReviewResponse } from "./types";

/** One cart per browser tab. Sessions live in backend memory, so this is not persisted. */
const sessionId = crypto.randomUUID();

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });

  if (!response.ok) {
    // The backend sends {detail: "..."}; fall back to the status when it does not.
    const body = await response.json().catch(() => null);
    throw new Error(body?.detail ?? `Request failed (${response.status})`);
  }
  return response.json() as Promise<T>;
}

export function chat(message: string) {
  return request<ChatResponse>("/api/chat", {
    method: "POST",
    body: JSON.stringify({ session_id: sessionId, message }),
  });
}

export function getCart() {
  return request<CartResponse>(`/api/cart/${sessionId}`);
}

export function removeItem(storeItemId: string) {
  return request<CartResponse>(
    `/api/cart/${sessionId}/items/${encodeURIComponent(storeItemId)}`,
    { method: "DELETE" },
  );
}

export function getReviews(modelNumber: string, brand: string) {
  const params = new URLSearchParams({ model_number: modelNumber });
  if (brand.trim()) params.set("brand", brand.trim());
  return request<ReviewResponse>(`/api/reviews?${params}`);
}
