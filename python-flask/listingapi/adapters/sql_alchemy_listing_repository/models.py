from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    TIMESTAMP,
    func,
)
from sqlalchemy.orm import declarative_base, relationship


Base = declarative_base()


class ListingModel(Base):
    __tablename__ = "listing"

    id: int = Column(Integer, primary_key=True, autoincrement=True)
    created_date: datetime = Column(
        DateTime, default=lambda: datetime.utcnow(), nullable=False
    )
    updated_date: datetime = Column(
        DateTime,
        default=lambda: datetime.utcnow(),
        onupdate=lambda: datetime.utcnow(),
        nullable=False,
    )

    # characteristics
    name: str = Column(String, nullable=False)
    description: str = Column(String, nullable=False)
    building_type: str = Column(String, nullable=False)
    surface_area_m2: float = Column(Float, nullable=False)
    rooms_count: int = Column(Integer, nullable=False)
    bedrooms_count: int = Column(Integer, nullable=False)

    # price
    price: float = Column(Float, nullable=False)

    # postal address
    street_address: str = Column(String, nullable=False)
    postal_code: str = Column(String, nullable=False)
    city: str = Column(String, nullable=False)
    country: str = Column(String, nullable=False)

    # contact
    contact_phone_number: Optional[str] = Column(String, nullable=True, default=None)

    # price history relationship
    price_history: list["ListingPriceHistoryModel"] = relationship(
        "ListingPriceHistoryModel",
        back_populates="listing",
        cascade="all, delete-orphan",
    )

    def to_dict(self) -> dict:
        listing_dict = {
            "id": self.id,
            "name": self.name,
            "postal_address": {
                "street_address": self.street_address,
                "postal_code": self.postal_code,
                "city": self.city,
                "country": self.country,
            },
            "description": self.description,
            "building_type": self.building_type,
            "latest_price_eur": self.price,
            "surface_area_m2": self.surface_area_m2,
            "rooms_count": self.rooms_count,
            "bedrooms_count": self.bedrooms_count,
            "contact_phone_number": self.contact_phone_number,
            "created_date": self.created_date.isoformat(),
            "updated_date": self.updated_date.isoformat(),
            "price_history": [price.to_dict() for price in self.price_history],
        }
        return listing_dict


class ListingPriceHistoryModel(Base):
    __tablename__ = "listing_price_history"

    id = Column(Integer, primary_key=True, autoincrement=True)
    listing_id = Column(Integer, ForeignKey(ListingModel.id), nullable=False)
    price = Column(Float, nullable=False)
    created_date = Column(TIMESTAMP, server_default=func.now(), nullable=False)

    # Define relationship with ListingModel
    listing = relationship("ListingModel", back_populates="price_history")

    def to_dict(self) -> dict:
        listing_price_history = {
            "id": self.id,
            "listing_id": self.listing_id,
            "price": self.price,
            "created_date": self.created_date.isoformat()
            if self.created_date
            else None,
        }
        return listing_price_history
