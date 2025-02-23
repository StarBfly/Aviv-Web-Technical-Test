from datetime import datetime

from pydantic import BaseModel


class ListingPriceHistory(BaseModel):
    id: int
    listing_id: int
    price: float
    created_date: datetime
