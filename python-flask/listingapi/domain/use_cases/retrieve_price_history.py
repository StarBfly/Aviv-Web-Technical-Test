from listingapi.domain import ports


class RetrieveListingsPriceHistory:
    def __init__(self, listing_repository: ports.ListingRepository):
        self.listing_repository = listing_repository

    def perform(self, id_: int) -> list[dict[str, float | str]]:
        """Get Listing price history by listing id."""
        listing = self.listing_repository.get(id_)

        price_history = [
            {"price_eur": price["price"], "created_date": price["created_date"]}
            for price in listing["price_history"]
        ]

        return price_history
