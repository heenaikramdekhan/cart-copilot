-- Review corpus schema: product identity plus the reviews that hang off it.
--
-- Postgres holds the review corpus, not a product catalog. Products here exist
-- only to be the join target for reviews and to carry the aggregate rating the
-- store APIs also report; live price and availability are never stored. Rows
-- are written by scripts/ingest_reviews.py and read by app/services/reviews.
--
-- Run once against a fresh database, then ingest, then data/seed/prune.sql.

create table products (
    -- The corpus product key. Reviews join on this, and the ingest upserts on
    -- it, so it is the primary key rather than a surrogate id.
    parent_asin   text primary key,
    title         text not null,
    brand         text,
    -- The join key to a live listing: corpus 'Item model number' against the
    -- store's mpn. Nullable because not every item carries one; find_reviews
    -- matches on it, so it is indexed.
    model_number  text,
    upc           text,
    category      text not null,   -- locked tier slug, e.g. 'pc-peripherals'
    -- Aggregates the store APIs also return, kept so a summary can state how
    -- many reviews back the corpus average.
    average_rating   double precision,
    rating_number    integer
);

create index products_model_number_idx on products (model_number);

create table reviews (
    parent_asin       text not null references products (parent_asin) on delete cascade,
    asin              text not null,   -- the specific variant reviewed
    user_id           text not null,
    rating            integer not null,
    title             text,
    body              text not null,
    helpful_vote      integer not null default 0,
    verified_purchase boolean not null,
    reviewed_at       timestamptz not null,
    -- The corpus's natural key for a review, and the ingest's upsert conflict
    -- target. The same (asin, user_id) pair recurs in the source, so this is
    -- what keeps a re-run from duplicating rows.
    primary key (asin, user_id)
);

-- Reviews are fetched and pruned by product, so index the join column.
create index reviews_parent_asin_idx on reviews (parent_asin);
