import { useState } from "react";
import { addItem, chat } from "../api";
import type { CartResponse, ChatResponse, Listing } from "../types";

type Props = { onCart: (cart: CartResponse) => void };

export default function ChatPanel({ onCart }: Props) {
  const [message, setMessage] = useState("");
  const [result, setResult] = useState<ChatResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function send(event: React.FormEvent) {
    event.preventDefault();
    if (!message.trim()) return;

    setBusy(true);
    setError(null);
    try {
      setResult(await chat(message));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  async function add(listing: Listing) {
    try {
      onCart(await addItem(listing));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  const requirements = result?.requirements;

  return (
    <section className="panel">
      <h2>What are you shopping for?</h2>

      <form onSubmit={send} className="row">
        <input
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="a wireless mouse under $60, must be bluetooth"
          aria-label="Shopping request"
        />
        <button type="submit" disabled={busy || !message.trim()}>
          {busy ? "Reading…" : "Send"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {requirements && (
        <div className="result">
          <h3>Understood as</h3>
          <dl>
            <dt>Category</dt>
            <dd>{requirements.category ?? <span className="muted">not stated</span>}</dd>

            <dt>Budget</dt>
            <dd>
              {requirements.budget === null ? (
                <span className="muted">not stated</span>
              ) : (
                `$${requirements.budget}`
              )}
            </dd>

            <dt>Must have</dt>
            <dd>
              {requirements.must_have.length ? (
                <ul className="tags">
                  {requirements.must_have.map((x) => (
                    <li key={x}>{x}</li>
                  ))}
                </ul>
              ) : (
                <span className="muted">nothing required</span>
              )}
            </dd>

            <dt>Nice to have</dt>
            <dd>
              {requirements.nice_to_have.length ? (
                <ul className="tags subtle">
                  {requirements.nice_to_have.map((x) => (
                    <li key={x}>{x}</li>
                  ))}
                </ul>
              ) : (
                <span className="muted">nothing optional</span>
              )}
            </dd>
          </dl>

          {result && result.ranked_products.length > 0 && (
            <>
              <h3>Top picks</h3>
              <ul className="items">
                {result.ranked_products.map((listing) => (
                  <li key={listing.store_item_id}>
                    <div>
                      <a href={listing.url} target="_blank" rel="noreferrer">
                        {listing.title}
                      </a>
                      <span className="muted">
                        {" "}
                        ${listing.price}
                        {listing.shipping_cost && ` + $${listing.shipping_cost} shipping`}
                        {listing.seller && ` · ${listing.seller}`}
                      </span>
                    </div>
                    <button onClick={() => add(listing)}>Add</button>
                  </li>
                ))}
              </ul>
              {result.ranked_products.some((l) => l.store === "catalog") && (
                <p className="notice">
                  Prices are from a Sept 2023 catalog snapshot. Live store search connects when its
                  API key is added.
                </p>
              )}
            </>
          )}

          {/* Say why the list is empty rather than implying the search found nothing. */}
          {result?.unavailable && <p className="notice">{result.unavailable}</p>}
        </div>
      )}
    </section>
  );
}
