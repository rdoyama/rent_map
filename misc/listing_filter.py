import logging
from typing import Any

from model.listing_model import Listing

logger = logging.getLogger(__name__)

class ListingFilter:

    def __init__(self, filters: Any):
        self.filters = filters

    def apply_filters(self, listings: list[Listing]) -> list[Listing]:
        rent_price_min, rent_price_max, neighborhood, pets_allowed, min_unit_floor, furnitured = self.get_filter_params()

        logger.info(f'Applying rent price filter - Min: {rent_price_min}, Max: {rent_price_max}')
        if neighborhood:
            logger.info(f'Applying neighborhood filter for "{neighborhood}"')
        else:
            logger.info(f'Neighborhood not selected - no filters will be applied for neighborhood')
        logger.info(f'PETS_ALLOWED filter: "{'' if pets_allowed else 'not '}allowed"')
        logger.info(f'Min floor filter: {min_unit_floor}')
        logger.info(f'Furnitured filter: {furnitured}')

        return list(filter(
            lambda listing: self.is_rent_price_ok(listing, rent_price_min, rent_price_max)
                            and self.is_neighborhood_ok(listing, neighborhood)
                            and self.is_pets_allowed(listing, pets_allowed)
                            and self.is_floor_ok(listing, min_unit_floor)
                            and self.is_furnitured(listing, furnitured)
            , listings
        ))

    @staticmethod
    def is_floor_ok(listing: Listing, min_unit_floor: int) -> bool:
        return listing.listing.unitFloor >= min_unit_floor

    @staticmethod
    def is_pets_allowed(listing: Listing, pets_allowed: bool) -> bool:
        # if no filter is provided, get all
        if not pets_allowed:
            return True
        return 'PETS_ALLOWED' in listing.listing.amenities

    @staticmethod
    def is_rent_price_ok(listing: Listing, rent_price_min: float = 0, rent_price_max: int = 9999999) -> bool:
        rent = listing.listing.get_rental_pricing_info()
        if rent is None:
            return False
        rent_price = rent.price
        return rent_price_min <= rent_price <= rent_price_max

    @staticmethod
    def is_neighborhood_ok(listing: Listing, neighborhood: str) -> bool:
        if not neighborhood:
            return True
        return listing.listing.address.neighborhood == neighborhood

    def get_filter_params(self) -> tuple:
        rent_price_min = self.filters['rent_price_min'].strip()
        rent_price_min = max(float(rent_price_min), 0) if rent_price_min.isdigit() else 0
        rent_price_max = self.filters['rent_price_max'].strip()
        rent_price_max = max(float(rent_price_max), 0) if rent_price_max.isdigit() else 9999999
        if rent_price_max <= rent_price_min:
            logger.error('rent_price_max must be greater than rent_price_min')
            raise Exception('rent_price_max must be greater than rent_price_min')
        neighborhood = self.filters['neighborhood'].strip()
        pets_allowed = True if self.filters['pets_allowed'].strip() == 'True' else False
        min_unit_floor_value = self.filters['min_unit_floor'].strip()
        min_unit_floor = max(int(min_unit_floor_value), 0) if min_unit_floor_value.isdigit() else 0
        furnitured_value = self.filters['furnitured'].strip()
        furnitured = True if furnitured_value == 'True' else False

        return rent_price_min, rent_price_max, neighborhood, pets_allowed, min_unit_floor, furnitured

    @staticmethod
    def is_furnitured(listing: Listing, furnitured: bool) -> bool:
        if not furnitured:
            return True
        return 'FURNITURED' in listing.listing.amenities