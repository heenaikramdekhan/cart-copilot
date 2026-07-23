-- Drop products the review agent cannot work with.
--
-- Run this once, after the ingest has finished. It is deliberately separate
-- from the ingest script: pruning needs the review count in the database, not
-- the count from one run, or a partial run deletes products that an earlier
-- run had already filled.
--
-- Reviews are removed automatically by the foreign key's on delete cascade.

delete from products p
where (select count(*) from reviews r where r.parent_asin = p.parent_asin) < 5;

select
    (select count(*) from products) as products,
    (select count(*) from reviews)  as reviews;
