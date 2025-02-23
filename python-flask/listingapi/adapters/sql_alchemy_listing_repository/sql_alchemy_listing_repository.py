from sqlalchemy import update
from sqlalchemy.orm import scoped_session

from listingapi.adapters.sql_alchemy_listing_repository import models
from listingapi.domain import entities, ports
from listingapi.domain.entities import exceptions


class SqlAlchemyListingRepository(ports.ListingRepository):
    def __init__(self, db_session: scoped_session):
        self.db_session = db_session

    def init(self) -> None:
        models.Base.metadata.create_all(self.db_session.get_bind())

    def create(self, listing: entities.ListingEntity) -> dict:
        listing_model = models.ListingModel(**listing.dict())
        self.db_session.add(listing_model)
        self.db_session.commit()
        price_history_id = models.ListingPriceHistoryModel(
            listing_id=listing_model.id,
            price=listing.latest_price_eur,
        )
        self.db_session.add(price_history_id)
        self.db_session.commit()
        data = listing_model.to_dict()
        return data

    def get_all(self) -> list[dict]:
        listing_models = self.db_session.query(models.ListingModel).all()
        listings = [listing.to_dict() for listing in listing_models]
        return listings

    def _get_listing_by_id(self, listing_id: int):
        existing_listing = self.db_session.get(models.ListingModel, listing_id)
        if existing_listing is None:
            raise exceptions.ListingNotFound

        return existing_listing

    def get_listing_by_id(self, listing_id: int) -> dict:
        listing = self._get_listing_by_id(listing_id)

        return listing.to_dict()

    def update(self, listing_id: int, listing: entities.ListingEntity) -> dict:
        sql_query = (
            update(models.ListingModel)
            .where(models.ListingModel.id == listing_id)
            .values(**listing.dict())
        )
        self.db_session.execute(sql_query)

        price_history_id = models.ListingPriceHistoryModel(
            listing_id=listing_id,
            price=listing.latest_price_eur,
        )
        self.db_session.add(price_history_id)
        self.db_session.commit()

        listing_model = self._get_listing_by_id(listing_id)
        listing_dict = listing_model.to_dict()
        return listing_dict
