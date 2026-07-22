import { useEffect, useState } from "react";
import { getCart, removeItem } from "../api";
import type { CartResponse } from "../types";

export default function CartPanel() {
  const [cart, setCart] = useState<CartResponse | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    getCart()
      .then(setCart)
      .catch((e) => setError(e instanceof Error ? e.message : String(e)));
  }, []);

  async function drop(storeItemId: string) {
    try {
      setCart(await removeItem(storeItemId));
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  return (
    <section className="panel">
      <h2>Your cart</h2>

      {error && <p className="error">{error}</p>}

      {cart?.items.length ? (
        <ul className="items">
          {cart.items.map((item) => (
            <li key={item.listing.store_item_id}>
              <div>
                <a href={item.listing.url} target="_blank" rel="noreferrer">
                  {item.listing.title}
                </a>
                <span className="muted">
                  {" "}
                  ${item.listing.price}
                  {item.listing.shipping_cost && ` + $${item.listing.shipping_cost} shipping`}
                  {item.listing.seller && ` · ${item.listing.seller}`}
                </span>
              </div>
              <button onClick={() => drop(item.listing.store_item_id)} aria-label="Remove">
                Remove
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <p className="notice">
          Your cart is empty. Items are added from search results, which arrive once the store API
          is connected.
        </p>
      )}

      {cart?.advice && <p className="advice">{cart.advice}</p>}

      {cart?.flags.length ? (
        <ul className="flags">
          {cart.flags.map((flag) => (
            <li key={flag.kind + flag.message}>
              <span className="kind">{flag.kind.replace(/_/g, " ")}</span>
              {flag.message}
              {flag.saves && <strong> saves ${flag.saves}</strong>}
            </li>
          ))}
        </ul>
      ) : null}
    </section>
  );
}
