import { removeItem } from "../api";
import type { CartResponse } from "../types";

type Props = {
  cart: CartResponse | null;
  error: string | null;
  onCart: (cart: CartResponse) => void;
  onError: (message: string) => void;
};

export default function CartPanel({ cart, error, onCart, onError }: Props) {
  async function drop(storeItemId: string) {
    try {
      onCart(await removeItem(storeItemId));
    } catch (e) {
      onError(e instanceof Error ? e.message : String(e));
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
          Your cart is empty. Add items from the search results on the left.
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

      {cart?.deals.length ? (
        <>
          <h3>Deals</h3>
          <ul className="flags">
            {cart.deals.map((deal) => {
              // Name the product from the cart rather than showing the raw id.
              const item = cart.items.find(
                (it) => it.listing.store_item_id === deal.store_item_id,
              );
              const title = item?.listing.title ?? deal.store_item_id;
              return (
                <li key={deal.store_item_id + deal.kind}>
                  {deal.kind === "coupon_available" ? (
                    <>
                      <span className="kind">coupon</span>
                      {title}
                      <span className="muted"> — coupon available at checkout</span>
                    </>
                  ) : (
                    <>
                      <span className="kind">markdown</span>
                      {title}
                      {deal.discount_percent !== null && (
                        <strong> {deal.discount_percent}% off</strong>
                      )}
                      {deal.original_price && (
                        <span className="muted"> (was ${deal.original_price})</span>
                      )}
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
