"""Parser tests for the Amazon Reviews 2023 corpus.

Field names and the category breadcrumb shape were verified against real records
streamed from the dataset; the junk model numbers below are real samples.
"""

from app.services.reviews.corpus import product_from_meta, review_from_record

META = {
    "parent_asin": "B0BS9SB6XM",
    "title": "Logitech MX Master 3S Wireless Performance Mouse",
    "store": "Logitech",
    "average_rating": 4.6,
    "rating_number": 12043,
    "categories": ["Electronics", "Computers & Accessories", "Computer Accessories & Peripherals"],
    "details": {
        "Item model number": "910-006556",
        "Package Dimensions": "5 x 3 x 2 inches",
    },
}

REVIEW = {
    "parent_asin": "B0BS9SB6XM",
    "asin": "B0BS9SB6XM",
    "user_id": "AE22236AFRRSMQIKGG7TPTB75QEA",
    "rating": 5.0,
    "title": "Best mouse I have owned",
    "text": "The scroll wheel alone justifies the price.",
    "helpful_vote": 14,
    "verified_purchase": True,
    "timestamp": 1673827200000,
}


def test_product_maps_identity_fields():
    product = product_from_meta(META)

    assert product["parent_asin"] == "B0BS9SB6XM"
    assert product["model_number"] == "910-006556"
    assert product["brand"] == "Logitech"
    assert product["category"] == "pc-peripherals"


def test_product_dropped_when_out_of_tier():
    """Amazon's Electronics is far broader than the locked tiers."""
    meta = {**META, "categories": ["Electronics", "Camera & Photo", "Accessories"]}

    assert product_from_meta(meta) is None


def test_product_dropped_without_any_identifier():
    meta = {**META, "details": {"Package Dimensions": "5 x 3 x 2 inches"}}

    assert product_from_meta(meta) is None


def test_free_text_rejected_as_model_number():
    """Real junk pulled from the corpus — none of these can match an eBay MPN."""
    for junk in ("Abstract Leaves", "SKT BN", "ARJK", "laptop backpack"):
        meta = {**META, "details": {"Item model number": junk}}

        assert product_from_meta(meta) is None, junk


def test_real_model_numbers_survive():
    for real in ("WD3200LPVT", "AF 24/1.8 FE", "P-SDU1TBV32100PRO-GE", "4651"):
        meta = {**META, "details": {"Item model number": real}}

        assert product_from_meta(meta)["model_number"] == real


def test_product_kept_with_upc_only():
    meta = {**META, "details": {"UPC": "097855172303 097855172310"}}

    product = product_from_meta(meta)

    assert product["upc"] == "097855172303"
    assert product["model_number"] is None


def test_price_extracted_as_fixed_point_string():
    assert product_from_meta({**META, "price": 98.4})["price"] == "98.40"
    assert product_from_meta({**META, "price": "$34.98"})["price"] == "34.98"


def test_unpriced_or_ambiguous_price_is_none():
    """Missing, empty, or a range — the corpus priced only some items."""
    assert product_from_meta(META)["price"] is None
    assert product_from_meta({**META, "price": ""})["price"] is None
    assert product_from_meta({**META, "price": "$10.00 - $20.00"})["price"] is None


def test_review_maps_fields_and_converts_epoch_millis():
    review = review_from_record(REVIEW)

    assert review["rating"] == 5
    assert review["asin"] == "B0BS9SB6XM"
    assert review["user_id"] == "AE22236AFRRSMQIKGG7TPTB75QEA"
    assert review["body"] == "The scroll wheel alone justifies the price."
    assert review["verified_purchase"] is True
    assert review["reviewed_at"].startswith("2023-01-16")


def test_null_bytes_and_surrogates_stripped():
    """Postgres text rejects both; real review bodies contain them."""
    review = review_from_record({**REVIEW, "text": "good\x00 mouse\ud800", "title": "ok\x00"})

    assert review["body"] == "good mouse"
    assert review["title"] == "ok"


def test_review_dropped_when_body_is_blank():
    """A star rating with no text gives Agent 4 nothing to summarize."""
    assert review_from_record({**REVIEW, "text": "   "}) is None
