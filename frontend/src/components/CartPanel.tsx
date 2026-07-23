import { removeItem } from "../api";
import type { CartResponse } from "../types";

type Props = {
  cart: CartResponse | null;
  error: string | null;
  onCart: (cart: CartResponse) => void;
  onError: (message: string) => void;
};

// How each flag reads: a saving (Pine) or something worth checking (Cobalt).
// Never an alarm. `kind` values come from app/agents/cart_optimization.py.
const FLAG_META: Record<string, { variant: string; label: string }> = {
  cheaper_elsewhere: { variant: "save", label: "Cheaper elsewhere" },
  shipping_consolidation: { variant: "save", label: "Combine shipping" },
  duplicate: { variant: "check", label: "Already in cart" },
};

function flagMeta(kind: string) {
  return FLAG_META[kind] ?? { variant: "check", label: kind.replace(/_/g, " ") };
}

export default function CartPanel({ cart, error, onCart, onError }: Props) {
  async function drop(storeItemId: string) {
    try {
      onCart(await removeItem(storeItemId));
    } catch (e) {
      onError(e instanceof Error ? e.message : String(e));
    }
  }

  return (
    <section className="panel tone-violet">
      <h2>Your cart</h2>
      <p className="sub">Cart Copilot reasons over the whole cart, not one item at a time.</p>

      {error && <p className="error">{error}</p>}

      {cart?.items.length ? (
        <ul className="items">
          {cart.items.map((item) => (
            <li key={item.listing.store_item_id}>
              <div className="item-info">
                <a className="item-title" href={item.listing.url} target="_blank" rel="noreferrer">
                  {item.listing.title}
                </a>
                <div className="item-meta">
                  <span className="price">${item.listing.price}</span>
                  {item.listing.shipping_cost && <span>+ ${item.listing.shipping_cost} shipping</span>}
                  {item.listing.seller && <span>· {item.listing.seller}</span>}
                </div>
              </div>
              <button className="remove" onClick={() => drop(item.listing.store_item_id)} aria-label="Remove">
                Remove
              </button>
            </li>
          ))}
        </ul>
      ) : (
        <p className="empty">
          <span className="emoji">🛒</span>
          Your cart is empty. Add options from the comparison to get suggestions.
        </p>
      )}

      {cart?.advice && <p className="advice">{cart.advice}</p>}

      {cart?.flags.length ? (
        <>
          <p className="section-label">What we noticed</p>
          <ul className="flags">
            {cart.flags.map((flag) => {
              const meta = flagMeta(flag.kind);
              return (
                <li key={flag.kind + flag.message} className={`flag ${meta.variant}`}>
                  <div className="flag-body">
                    <span className="flag-kind">{meta.label}</span>
                    <p className="flag-msg">{flag.message}</p>
                  </div>
                  {flag.saves && (
                    <span className="delta">
                      ${flag.saves}
                      <small>saved</small>
                    </span>
                  )}
                </li>
              );
            })}
          </ul>
        </>
      ) : null}

      {cart?.deals.length ? (
        <>
          <p className="section-label">Deals</p>
          <ul className="deals">
            {cart.deals.map((deal) => {
              const item = cart.items.find(
                (it) => it.listing.store_item_id === deal.store_item_id,
              );
              const title = item?.listing.title ?? deal.store_item_id;
              return (
                <li key={deal.store_item_id + deal.kind} className="deal">
                  {deal.kind === "coupon_available" ? (
                    <>
                      <span className="deal-badge">Coupon</span>
                      <span>
                        {title} <span className="muted">available at checkout</span>
                      </span>
                    </>
                  ) : (
                    <>
                      <span className="deal-badge">Deal</span>
                      <span>
                        {title}
                        {deal.discount_percent !== null && <strong> {deal.discount_percent}% off</strong>}
                        {deal.original_price && <span className="muted"> (was ${deal.original_price})</span>}
                      </span>
                    </>
                  )}
                </li>
              );
            })}
          </ul>
        </>
      ) : null}
    </section>
  );
}
