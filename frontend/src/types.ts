/** Mirrors the backend's shared agent state. Keep in sync with app/graph/state.py. */

/** Money arrives as a string: the backend uses Decimal so cents cannot drift. */
export type Money = string;

export type Requirements = {
  category: string | null;
  budget: number | null;
  must_have: string[];
  nice_to_have: string[];
};

export type Listing = {
  store: string;
  store_item_id: string;
  title: string;
  price: Money;
  currency: string;
  url: string;
  shipping_cost: Money | null;
  condition: string | null;
  seller: string | null;
  image_url: string | null;
  original_price: Money | null;
  discount_percent: number | null;
  has_coupon: boolean;
  gtin: string | null;
  mpn: string | null;
  brand: string | null;
  aspects: Record<string, string>;
};

export type CartItem = { listing: Listing; quantity: number };

export type CartFlag = {
  kind: string;
  message: string;
  /** Null when the rule proved a problem but not a figure. */
  saves: Money | null;
};

export type CartResponse = {
  items: CartItem[];
  flags: CartFlag[];
  advice: string | null;
};

export type ChatResponse = {
  requirements: Requirements;
  ranked_products: Listing[];
  /** Set when a step could not run, so the UI can say why rather than imply no results. */
  unavailable: string | null;
};

export type ReviewSummary = {
  pros: string[];
  cons: string[];
  /** How many real reviews back this summary. */
  based_on: number;
  /** How recent the corpus is. */
  corpus_through: string;
  average_rating: number | null;
};

export type ReviewResponse = {
  product_title: string;
  matched_on: string;
  summary: ReviewSummary;
};
