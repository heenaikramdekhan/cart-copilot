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
              {/* A cart whose contents are the comparison value-bars. */}
              <svg
                viewBox="0 0 24 24"
                fill="none"
                stroke="#fff"
                strokeWidth="1.7"
                strokeLinecap="round"
                strokeLinejoin="round"
              >
                <rect x="8.3" y="9.5" width="1.7" height="4.5" rx="0.6" fill="#fff" stroke="none" />
                <rect x="11.3" y="7" width="1.7" height="7" rx="0.6" fill="#fff" stroke="none" />
                <rect x="14.3" y="10.5" width="1.7" height="3.5" rx="0.6" fill="#fff" stroke="none" />
                <path d="M2.5 2.5h2l2.66 12.42a2 2 0 0 0 2 1.58h9.78a2 2 0 0 0 1.95-1.57l1.65-7.43H5.5" />
                <circle cx="9" cy="20.4" r="1.1" />
                <circle cx="18.4" cy="20.4" r="1.1" />
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
