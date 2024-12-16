import pytest

from app.receipt_scorer import Receipt, ReceiptScorer

RECEIPT_EXAMPLE_TARGET = {
    "retailer": "Target",
    "purchaseDate": "2022-01-01",
    "purchaseTime": "13:01",
    "items": [
        {"shortDescription": "Mountain Dew 12PK", "price": "6.49"},
        {"shortDescription": "Emils Cheese Pizza", "price": "12.25"},
        {"shortDescription": "Knorr Creamy Chicken", "price": "1.26"},
        {"shortDescription": "Doritos Nacho Cheese", "price": "3.35"},
        {"shortDescription": "   Klarbrunn 12-PK 12 FL OZ  ", "price": "12.00"},
    ],
    "total": "35.35",
}

RECEIPT_EXAMPLE_MM_CORNER = {
    "retailer": "M&M Corner Market",
    "purchaseDate": "2022-03-20",
    "purchaseTime": "14:33",
    "items": [
        {"shortDescription": "Gatorade", "price": "2.25"},
        {"shortDescription": "Gatorade", "price": "2.25"},
        {"shortDescription": "Gatorade", "price": "2.25"},
        {"shortDescription": "Gatorade", "price": "2.25"},
    ],
    "total": "9.00",
}

RECEIPT_EXAMPLE_MM_CORNER_2PM = RECEIPT_EXAMPLE_MM_CORNER.copy()
RECEIPT_EXAMPLE_MM_CORNER_2PM["purchaseTime"] = "14:00"

RECEIPT_EXAMPLE_MM_CORNER_4PM = RECEIPT_EXAMPLE_MM_CORNER.copy()
RECEIPT_EXAMPLE_MM_CORNER_4PM["purchaseTime"] = "16:00"


def test_score_receipt_target_returns_correct_points():
    """First scoring example from https://github.com/fetch-rewards/receipt-processor-challenge"""

    r = Receipt(**RECEIPT_EXAMPLE_TARGET)

    scorer = ReceiptScorer(r)

    # Check intermediate scores match github example
    assert scorer._score_retailer_name_alphanumeric() == 6
    assert scorer._score_total_dollar_increment() == 0
    assert scorer._score_total_quarter_increment() == 0
    assert scorer._score_items_count_every_two() == 10
    assert scorer._score_items_description_length_multiple_of_three() == 6
    assert scorer._score_purchase_date_odd_day() == 6
    assert scorer._score_purchase_time() == 0

    assert scorer.calculate_score() == 28


def test_score_receipt_mm_corner_returns_correct_points():
    """Second scoring example from https://github.com/fetch-rewards/receipt-processor-challenge"""

    r = Receipt(**RECEIPT_EXAMPLE_MM_CORNER)

    scorer = ReceiptScorer(r)

    # Check intermediate scores match github example
    assert scorer._score_retailer_name_alphanumeric() == 14
    assert scorer._score_total_dollar_increment() == 50
    assert scorer._score_total_quarter_increment() == 25
    assert scorer._score_items_count_every_two() == 10
    assert scorer._score_items_description_length_multiple_of_three() == 0
    assert scorer._score_purchase_date_odd_day() == 0
    assert scorer._score_purchase_time() == 10

    # Check total score matches github example
    assert scorer.calculate_score() == 109


@pytest.mark.parametrize(
    "receipt,expected_total_score,description",
    [
        (RECEIPT_EXAMPLE_TARGET, 28, "Github receipt example #1"),
        (RECEIPT_EXAMPLE_MM_CORNER, 109, "Github receipt example #2"),
        (
            RECEIPT_EXAMPLE_MM_CORNER_2PM,
            99,
            "2PM should not contribute to time of day score",
        ),
        (
            RECEIPT_EXAMPLE_MM_CORNER_4PM,
            99,
            "4PM should not contribute to time of day score",
        ),
        (
            {
                "retailer": "FOO",
                "purchaseDate": "2022-03-20",
                "purchaseTime": "12:00",
                "items": [{"shortDescription": "FIZZ", "price": "1.00"}],
                "total": "1.00",
            },
            78,  # 25 cent and 1 dollar multiple, 3 alphanumberic in retailer
            "Only one item in list",
        ),
    ],
)
def test_score_receipt_totals(receipt, expected_total_score, description):
    """Test different boundary scenarios."""
    r = Receipt(**receipt)

    scorer = ReceiptScorer(r)

    assert (
        scorer.calculate_score() == expected_total_score
    ), f"Expected total score mismatched for receipt testing {description}."
