import { useEffect, useState } from "react";
import { getCart } from "./api";
import CartPanel from "./components/CartPanel";
import ChatPanel from "./components/ChatPanel";
import ReviewPanel from "./components/ReviewPanel";
import type { CartResponse } from "./types";
import "./styles.css";

export default function App() {
  // The cart is shared: search adds to it, the cart panel removes from it, so
  // it lives here and both panels update the same copy.
  const [cart, setCart] = useState<CartResponse | null>(null);
  const [cartError, setCartError] = useState<string | null>(null);

  useEffect(() => {
    getCart()
      .then(setCart)
      .catch((e) => setCartError(e instanceof Error ? e.message : String(e)));
  }, []);

  return (
    <div className="app">
      <header>
        <h1>Cart Copilot</h1>
        <p>
          Real listings, real reviews. Nothing here is invented: the review text comes from 141,240
          customer reviews, and prices come from live store listings.
        </p>
      </header>

      <main>
        <div className="column">
          <ChatPanel onCart={setCart} />
          <ReviewPanel />
        </div>
        <div className="column">
          <CartPanel cart={cart} error={cartError} onCart={setCart} onError={setCartError} />
        </div>
      </main>
    </div>
  );
}
