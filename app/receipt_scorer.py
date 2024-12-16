from datetime import datetime
from math import ceil
from typing import List

from pydantic import BaseModel, Field

from app.models import Item, Receipt


class ReceiptScorer:
    def __init__(self, receipt: Receipt):
        self.receipt = receipt

    def calculate_score(self) -> int:
        """Calculate the overall score of the receipt."""
        score = 0
        score += self._score_retailer_name_alphanumeric()
        score += self._score_total_dollar_increment()
        score += self._score_total_quarter_increment()
        score += self._score_items_count_every_two()
        score += self._score_items_description_length_multiple_of_three()
        score += self._score_purchase_date_odd_day()
        score += self._score_purchase_time()
        return score

    def _score_retailer_name_alphanumeric(self) -> int:
        """One point for every alphanumeric character in the retailer name."""
        return sum(1 for char in self.receipt.retailer if char.isalnum())

    def _score_total_dollar_increment(self) -> int:
        """50 points if the total is a round dollar amount with no cents."""
        total = float(self.receipt.total)
        return 50 if total.is_integer() else 0

    def _score_total_quarter_increment(self) -> int:
        """25 points if the total is a multiple of 0.25."""
        total = float(self.receipt.total)
        return 25 if (total * 100) % 25 == 0 else 0

    def _score_items_count_every_two(self) -> int:
        """5 points for every two items on the receipt."""
        return (len(self.receipt.items) // 2) * 5

    def _score_items_description_length_multiple_of_three(self) -> int:
        """If the trimmed length of the item description is a multiple of 3, multiply the price by 0.2 and round up to the nearest integer."""
        score = 0
        for item in self.receipt.items:
            price = float(item.price)
            description = item.shortDescription.strip()

            if len(description) % 3 == 0:
                score += ceil(price * 0.2)

        return score

    def _score_purchase_date_odd_day(self) -> int:
        """6 points if the day in the purchase date is odd."""
        try:
            day = int(self.receipt.purchaseDate.split("-")[-1])
            return 6 if day % 2 == 1 else 0
        except ValueError:
            return 0

    def _score_purchase_time(self) -> int:
        """10 points if the time of purchase is after 2:00pm and before 4:00pm."""
        try:
            receipt_time = datetime.strptime(self.receipt.purchaseTime, "%H:%M").time()

            start_time = datetime.strptime("14:00", "%H:%M").time()
            end_time = datetime.strptime("16:00", "%H:%M").time()

            if start_time < receipt_time < end_time:
                return 10
            return 0
        except ValueError:
            return 0
