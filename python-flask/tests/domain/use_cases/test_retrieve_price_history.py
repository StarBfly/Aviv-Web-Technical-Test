from freezegun import freeze_time

from listingapi.domain import use_cases
from tests import factories


class TestRetriveListingsPriceHistory:
    @freeze_time("2023-01-18 08:50:03.761691")
    def test_get_history(
        self,
        persist_listing_use_case: use_cases.PersistListing,
        update_listing_use_case: use_cases.UpdateListing,
        retrieve_history_use_case: use_cases.RetrieveListingsPriceHistory,
    ) -> None:
        listing_entity = (
            factories.entities.Listing()
            .with_name("Mikhail Schmiedt")
            .with_price(512000.0)
            .build()
        )
        persisted_listing = persist_listing_use_case.listing_repository.create(
            listing_entity
        )

        listing_entity.name = "My new name"
        listing_entity.latest_price_eur = 800000.0
        with freeze_time("2023-01-19 08:50:03.761691"):
            update_listing_use_case.perform(persisted_listing["id"], listing_entity)

        history = retrieve_history_use_case.perform(persisted_listing["id"])

        assert len(history) == 2
        assert history[0]["price_eur"] == 512000.0
        assert history[1]["price_eur"] == 800000.0
