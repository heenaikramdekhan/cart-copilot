import { useState } from "react";
import { addItem } from "../api";
import type { CartResponse, ChatResponse, Listing } from "../types";

type Props = {
  result: ChatResponse | null;
  onCart: (cart: CartResponse) => void;
};

export default function ComparisonTable({ result, onCart }: Props) {
  const [addedId, setAddedId] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function add(listing: Listing) {
    try {
      onCart(await addItem(listing));
      setAddedId(listing.store_item_id);
      window.setTimeout(
        () => setAddedId((cur) => (cur === listing.store_item_id ? null : cur)),
        1400,
      );
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e));
    }
  }

  if (!result) {
    return (
      <section className="panel tone-pine">
        <h2>Compare</h2>
        <p className="sub">Search on the left and the strongest options land here, side by side.</p>
        <p className="empty">
          <span className="emoji">⚖️</span>
          Nothing to compare yet. Run a search to see options ranked by fit, then price.
        </p>
      </section>
    );
  }

  const products = result.ranked_products;
  const prices = products.map((p) => Number(p.price));
  const minPrice = Math.min(...prices);
  const maxPrice = Math.max(...prices);
  // A fuller bar means a better price: the cheapest fills, the dearest barely does.
  const priceValue = (p: number) => (maxPrice === minPrice ? 1 : (maxPrice - p) / (maxPrice - minPrice));

  return (
    <section className="panel tone-pine">
      <h2>Compare</h2>
      <p className="sub">Ranked by how well they fit your request, then price.</p>

      {error && <p className="error">{error}</p>}

      {products.length === 0 ? (
        <p className="notice">{result.unavailable ?? "No options matched your request."}</p>
      ) : (
        <>
          <p className="compare-meta">
            {products.length} options · ${minPrice} to ${maxPrice}
          </p>

          <div className="compare-head">
            <span>Product</span>
            <span>Price</span>
            <span>Rating</span>
            <span />
          </div>

          {products.map((l) => {
            const price = Number(l.price);
            const isBest = price === minPrice;
            return (
              <div className={isBest ? "crow best" : "crow"} key={l.store_item_id}>
                <div className="cprod">
                  {isBest && <span className="tab">Best value</span>}
                  <a className="item-title" href={l.url} target="_blank" rel="noreferrer">
                    {l.title}
                  </a>
                  <span className="cmeta mono">
                    {[l.brand, l.mpn].filter(Boolean).join(" · ") || "no model listed"}
                  </span>
                </div>

                <div className="cvalue" data-label="Price">
                  <span className="price">${l.price}</span>
                  <div className={isBest ? "vbar best" : "vbar"}>
                    <i style={{ width: `${Math.round(priceValue(price) * 100)}%` }} />
                  </div>
                  <span className="cnote">
                    {l.shipping_cost ? `+ $${l.shipping_cost} shipping` : "shipping n/a"}
                    {l.condition ? ` · ${l.condition}` : ""}
                  </span>
                </div>

                <div className="cvalue" data-label="Rating">
                  {l.rating != null ? (
                    <>
                      <span className="price">
                        {l.rating.toFixed(1)}
                        <span className="cnote"> / 5</span>
                      </span>
                      <div className="vbar">
                        <i style={{ width: `${Math.round((l.rating / 5) * 100)}%` }} />
                      </div>
                      <span className="cnote">
                        {l.rating_count ? `${l.rating_count.toLocaleString()} ratings` : ""}
                      </span>
                    </>
                  ) : (
                    <span className="muted">not rated</span>
                  )}
                </div>

                <div className="cadd">
                  <button
                    className={addedId === l.store_item_id ? "add added" : "add"}
                    onClick={() => add(l)}
                  >
                    {addedId === l.store_item_id ? "Added ✓" : "Add"}
                  </button>
                </div>
              </div>
            );
          })}

          {products.some((l) => l.store === "catalog") && (
            <p className="notice">
              Prices are from a Sept 2023 catalog snapshot. Live store search connects once a store
              API key is added.
            </p>
          )}
        </>
      )}
    </section>
  );
}
