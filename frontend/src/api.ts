import type { CartResponse, ChatResponse, Listing, ReviewResponse } from "./types";

/** One cart per browser tab. Sessions live in backend memory, so this is not persisted. */
const sessionId = crypto.randomUUID();

// Empty in dev (Vite proxies /api to the backend); set to the backend's URL in
// production via the VITE_API_BASE build-time env var.
const API_BASE = import.meta.env.VITE_API_BASE ?? "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
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

export function addItem(listing: Listing, quantity = 1) {
  return request<CartResponse>(`/api/cart/${sessionId}/items`, {
    method: "POST",
    body: JSON.stringify({ listing, quantity }),
  });
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
