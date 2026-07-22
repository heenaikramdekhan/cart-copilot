import { useState } from "react";
import { chat } from "../api";
import type { ChatResponse } from "../types";

export default function ChatPanel() {
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

          {/* Say why the list is empty rather than implying the search found nothing. */}
          {result?.unavailable && <p className="notice">{result.unavailable}</p>}
        </div>
      )}
    </section>
  );
}
