import type { Session } from "@supabase/supabase-js";
import { useEffect, useState } from "react";
import { getCart } from "./api";
import CartPanel from "./components/CartPanel";
import ChatPanel from "./components/ChatPanel";
import ComparisonTable from "./components/ComparisonTable";
import Landing from "./components/Landing";
import Logo from "./components/Logo";
import ReviewPanel from "./components/ReviewPanel";
import { supabase } from "./supabase";
import type { CartResponse, ChatResponse } from "./types";
import "./styles.css";

export default function App() {
  const [session, setSession] = useState<Session | null>(null);
  const [authReady, setAuthReady] = useState(false);
  const [result, setResult] = useState<ChatResponse | null>(null);
  const [cart, setCart] = useState<CartResponse | null>(null);
  const [cartError, setCartError] = useState<string | null>(null);

  // Track the auth session; the listener reveals or hides the app on its own.
  useEffect(() => {
    supabase.auth.getSession().then(({ data }) => {
      setSession(data.session);
      setAuthReady(true);
    });
    const { data } = supabase.auth.onAuthStateChange((_event, next) => setSession(next));
    return () => data.subscription.unsubscribe();
  }, []);

  // Load the cart once signed in.
  useEffect(() => {
    if (!session) return;
    getCart()
      .then(setCart)
      .catch((e) => setCartError(e instanceof Error ? e.message : String(e)));
  }, [session]);

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

  if (!authReady) {
    return (
      <>
        <div className="bg-glow" aria-hidden="true" />
        <div className="app">
          <p className="loading">Loading…</p>
        </div>
      </>
    );
  }

  if (!session) {
    return (
      <>
        <div className="bg-glow" aria-hidden="true" />
        <Landing />
      </>
    );
  }

  return (
    <>
      <div className="bg-glow" aria-hidden="true" />
      <div className="app">
        <header className="hero">
          <div className="hero-top">
            <h1 className="brand">
              <Logo />
              <span className="brand-name">Cart Copilot</span>
            </h1>
            <div className="account">
              <span className="account-email mono">
                {session.user.user_metadata?.name || session.user.email}
              </span>
              <button className="ghost" onClick={() => supabase.auth.signOut()}>
                Sign out
              </button>
            </div>
          </div>
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
