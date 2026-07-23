import { useEffect, useState } from "react";
import { getCart } from "./api";
import CartPanel from "./components/CartPanel";
import ChatPanel from "./components/ChatPanel";
import ComparisonTable from "./components/ComparisonTable";
import ReviewPanel from "./components/ReviewPanel";
import type { CartResponse, ChatResponse } from "./types";
import "./styles.css";

export default function App() {
  const [result, setResult] = useState<ChatResponse | null>(null);
  const [cart, setCart] = useState<CartResponse | null>(null);
  const [cartError, setCartError] = useState<string | null>(null);

  useEffect(() => {
    getCart()
      .then(setCart)
      .catch((e) => setCartError(e instanceof Error ? e.message : String(e)));
  }, []);

  // Feed the cursor position to the interactive background glow.
  useEffect(() => {
    let raf = 0;
    const move = (e: MouseEvent) => {
      cancelAnimationFrame(raf);
      raf = requestAnimationFrame(() => {
        const root = document.documentElement.style;
        root.setProperty("--mx", `${e.clientX}px`);
        root.setProperty("--my", `${e.clientY}px`);
      });
    };
    window.addEventListener("mousemove", move);
    return () => {
      window.removeEventListener("mousemove", move);
      cancelAnimationFrame(raf);
    };
  }, []);

  return (
    <>
      <div className="bg-glow" aria-hidden="true" />
      <div className="app">
        <header className="hero">
          <h1 className="brand">
            <span className="logo" aria-hidden="true">
              {/* Signature mark: a value bar with a marker, where an option sits. */}
              <svg viewBox="0 0 24 24" fill="none">
                <rect x="3" y="10.4" width="18" height="3.2" rx="1.6" fill="rgba(255,255,255,0.45)" />
                <rect x="3" y="10.4" width="10.5" height="3.2" rx="1.6" fill="#fff" />
                <circle cx="13.5" cy="12" r="3.4" fill="#fff" stroke="#0e6b59" strokeWidth="1.6" />
              </svg>
            </span>
            <span className="brand-name">Cart Copilot</span>
          </h1>
          <p className="tagline">
            An AI assistant that reasons over your whole cart, catching savings, spec mismatches, and
            shipping you pay for twice.
          </p>
          <p className="trust">Real data only. 141,240 genuine customer reviews and real prices.</p>
        </header>

        <div className="grid">
          <div className="col-main">
            <ChatPanel result={result} onResult={setResult} />
            <ComparisonTable result={result} onCart={setCart} />
          </div>
          <div className="col-side">
            <CartPanel cart={cart} error={cartError} onCart={setCart} onError={setCartError} />
            <ReviewPanel />
          </div>
        </div>
      </div>
    </>
  );
}
