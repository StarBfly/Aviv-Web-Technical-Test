from typing import Optional

from pydantic import BaseModel

from listingapi.domain.entities.postal_address import PostalAddressEntity


class ListingEntity(BaseModel):
    name: str
    postal_address: PostalAddressEntity
    description: str
    building_type: str
    latest_price_eur: float
    surface_area_m2: int
    rooms_count: int
    bedrooms_count: int
    contact_phone_number: Optional[str]

    def dict(self, *args, **kwargs) -> dict:
        """Custom dictionary serialization for ListingModel."""
        data: dict = super().dict(*args, **kwargs)

        # flaten out the postal address property
        for key, value in data["postal_address"].items():
            data[key] = value

        data["price"] = data["latest_price_eur"]
        data.pop("postal_address")
        data.pop("latest_price_eur")
        return data
