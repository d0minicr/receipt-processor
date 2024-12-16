from typing import List

from pydantic import BaseModel, Field


class Item(BaseModel):
    shortDescription: str = Field(
        ...,
        pattern=r"^[\w\s\-]+$",
        description="The short product description for the item.",
        example="Mountain Dew 12PK",
    )
    price: str = Field(
        ...,
        pattern=r"^\d+\.\d{2}$",
        description="The total price paid for this item.",
        example="6.49",
    )


class Receipt(BaseModel):
    retailer: str = Field(
        ...,
        pattern=r"^[\w\s\-\&]+$",
        description="The name of the retailer or store the receipt is from.",
        example="M&M Corner Market",
    )
    purchaseDate: str = Field(
        ...,
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="The date of the purchase printed on the receipt.",
        example="2022-01-01",
    )
    purchaseTime: str = Field(
        ...,
        pattern=r"^\d{2}:\d{2}$",
        description="The time of the purchase in 24-hour format.",
        example="13:01",
    )
    items: List[Item] = Field(
        ..., min_length=1, description="The list of items in the receipt."
    )
    total: str = Field(
        ...,
        pattern=r"^\d+\.\d{2}$",
        description="The total amount paid on the receipt.",
        example="6.49",
    )
