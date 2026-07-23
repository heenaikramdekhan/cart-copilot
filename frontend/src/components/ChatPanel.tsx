import { useRef, useState } from "react";
import { chat } from "../api";
import type { ChatResponse } from "../types";

type Props = {
  result: ChatResponse | null;
  onResult: (result: ChatResponse | null) => void;
};

const SUGGESTIONS = ["wireless mouse", "mechanical keyboard", "usb hub", "gaming headset"];

export default function ChatPanel({ result, onResult }: Props) {
  const [message, setMessage] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  async function runSearch(query: string) {
    if (!query.trim()) return;
    setBusy(true);
    setError(null);
    try {
      onResult(await chat(query));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  function send(event: React.FormEvent) {
    event.preventDefault();
    runSearch(message);
  }

  function pick(query: string) {
    setMessage(query);
    runSearch(query);
  }

  // Reset for a fresh search: clears the box and the results, keeps the cart.
  function clearSearch() {
    setMessage("");
    setError(null);
    onResult(null);
    inputRef.current?.focus();
  }

  const requirements = result?.requirements;

  return (
    <section className="panel tone-cobalt">
      <h2>What are you shopping for?</h2>
      <p className="sub">Describe it in plain English. Budget, must haves, all of it.</p>

      <form onSubmit={send} className="row">
        <input
          ref={inputRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="a wireless mouse under $40, must be bluetooth"
          aria-label="Shopping request"
        />
        <button type="submit" disabled={busy || !message.trim()}>
          {busy ? "Searching…" : "Search"}
        </button>
        {(result || message) && (
          <button type="button" className="ghost" onClick={clearSearch} disabled={busy}>
            Clear
          </button>
        )}
      </form>

      <div className="chips">
        <span className="chips-label">Try</span>
        {SUGGESTIONS.map((q) => (
          <button type="button" key={q} className="chip" onClick={() => pick(q)} disabled={busy}>
            {q}
          </button>
        ))}
      </div>

      {error && <p className="error">{error}</p>}

      {requirements && (
        <div className="result">
          <p className="section-label">Understood as</p>
          <dl>
            <dt>Category</dt>
            <dd>{requirements.category ?? <span className="muted">not stated</span>}</dd>

            <dt>Budget</dt>
            <dd>
              {requirements.budget === null ? (
                <span className="muted">not stated</span>
              ) : (
                <span className="mono">${requirements.budget}</span>
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
        </div>
      )}
    </section>
  );
}
