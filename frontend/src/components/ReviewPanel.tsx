import { useState } from "react";
import { getReviews } from "../api";
import type { ReviewResponse } from "../types";

export default function ReviewPanel() {
  const [brand, setBrand] = useState("Plugable");
  const [model, setModel] = useState("USB3-SWITCH2");
  const [result, setResult] = useState<ReviewResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  async function look(event: React.FormEvent) {
    event.preventDefault();
    if (!model.trim()) return;

    setBusy(true);
    setError(null);
    setResult(null);
    try {
      setResult(await getReviews(model, brand));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <section className="panel">
      <h2>What buyers actually said</h2>

      <form onSubmit={look} className="row">
        <input
          value={brand}
          onChange={(e) => setBrand(e.target.value)}
          placeholder="Brand"
          aria-label="Brand"
        />
        <input
          value={model}
          onChange={(e) => setModel(e.target.value)}
          placeholder="Model number"
          aria-label="Model number"
        />
        <button type="submit" disabled={busy || !model.trim()}>
          {busy ? "Reading…" : "Look up"}
        </button>
      </form>

      {error && <p className="error">{error}</p>}

      {result && (
        <div className="result">
          <h3>{result.product_title}</h3>

          {/* Provenance sits with the summary: a reader is entitled to know how
              much evidence is behind it and how old that evidence is. */}
          <p className="provenance">
            From <strong>{result.summary.based_on}</strong> real reviews
            {result.summary.average_rating !== null && (
              <> · averaging {result.summary.average_rating} / 5</>
            )}{" "}
            · matched on {result.matched_on.replace(/_/g, " ")} · reviews up to{" "}
            {result.summary.corpus_through}
          </p>

          <div className="verdict">
            <div>
              <h4 className="good">Praised</h4>
              <ul>
                {result.summary.pros.map((x) => (
                  <li key={x}>{x}</li>
                ))}
              </ul>
            </div>
            <div>
              <h4 className="bad">Complained about</h4>
              <ul>
                {result.summary.cons.map((x) => (
                  <li key={x}>{x}</li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}
    </section>
  );
}
