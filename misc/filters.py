from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from configparser import SectionProxy
from dataclasses import dataclass
from typing import Any, Iterable

from model.listing_model import Listing

log = logging.getLogger(__name__)


def _parse_float(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    return float(text)


def _parse_int(value: Any) -> int | None:
    if value is None:
        return None
    text = str(value).strip()
    if text == "":
        return None
    return int(text)


def _parse_bool(value: Any) -> bool | None:
    if value is None:
        return None
    text = str(value).strip().lower()
    if text == "":
        return None
    if text == "true":
        return True
    if text == "false":
        return False
    raise ValueError(f"Invalid boolean value: {value}")


@dataclass(slots=True)
class FilterCriteria:
    price_min: float | None = None
    price_max: float | None = None
    pets_allowed: bool | None = None
    min_unit_floor: int | None = None
    furnished: bool | None = None

    @classmethod
    def from_config(cls, config: SectionProxy) -> "FilterCriteria":
        criteria = cls(
            price_min=_parse_float(config.get("rent_price_min")),
            price_max=_parse_float(config.get("rent_price_max")),
            pets_allowed=_parse_bool(config.get("pets_allowed")),
            min_unit_floor=_parse_int(config.get("min_unit_floor")),
            furnished=_parse_bool(config.get("furnished")),
        )
        criteria.validate()
        return criteria

    def validate(self) -> None:
        if self.price_min is not None and self.price_min < 0:
            raise ValueError("rent_price_min must be >= 0")
        if self.price_max is not None and self.price_max < 0:
            raise ValueError("rent_price_max must be >= 0")
        if (
            self.price_min is not None
            and self.price_max is not None
            and self.price_min > self.price_max
        ):
            raise ValueError("rent_price_min must be <= rent_price_max")
        if self.min_unit_floor is not None and self.min_unit_floor < 0:
            raise ValueError("min_unit_floor must be >= 0")


class ListingFilter(ABC):
    @abstractmethod
    def matches(self, listing: Listing) -> bool:
        raise NotImplementedError


class PriceFilter(ListingFilter):
    def __init__(self, price_min: float | None, price_max: float | None):
        self.price_min = price_min
        self.price_max = price_max

    def matches(self, listing: Listing) -> bool:
        listing_obj = listing.listing
        if listing_obj is None:
            return False

        total_price = listing_obj.get_total_price()
        if self.price_min is not None and total_price < self.price_min:
            return False
        if self.price_max is not None and total_price > self.price_max:
            return False
        return True


class AmenityFilter(ListingFilter):
    def __init__(self, amenity: str, required: bool):
        self.amenity = amenity
        self.required = required

    def matches(self, listing: Listing) -> bool:
        listing_obj = listing.listing
        if listing_obj is None:
            return False

        amenities = listing_obj.amenities or ()
        has_amenity = self.amenity in amenities
        return has_amenity if self.required else not has_amenity


class MinFloorFilter(ListingFilter):
    def __init__(self, min_floor: int):
        self.min_floor = min_floor

    def matches(self, listing: Listing) -> bool:
        listing_obj = listing.listing
        if listing_obj is None:
            return False
        return listing_obj.unitFloor >= self.min_floor


def build_filters(criteria: FilterCriteria) -> list[ListingFilter]:
    filters: list[ListingFilter] = []

    if criteria.price_min is not None or criteria.price_max is not None:
        filters.append(PriceFilter(criteria.price_min, criteria.price_max))

    if criteria.pets_allowed is not None:
        filters.append(AmenityFilter("PETS_ALLOWED", criteria.pets_allowed))

    if criteria.min_unit_floor is not None:
        filters.append(MinFloorFilter(criteria.min_unit_floor))

    if criteria.furnished is not None:
        filters.append(AmenityFilter("FURNISHED", criteria.furnished))

    return filters


class ListingFilterEngine:
    def __init__(self, filters: Iterable[ListingFilter]):
        self.filters = list(filters)

    @classmethod
    def from_config(cls, config: SectionProxy) -> "ListingFilterEngine":
        criteria = FilterCriteria.from_config(config)
        log.info("Initialized filter engine with criteria: %s", criteria)
        return cls(build_filters(criteria))

    def matches(self, listing: Listing) -> bool:
        return all(filter_.matches(listing) for filter_ in self.filters)

    def apply(self, listings: list[Listing]) -> list[Listing]:
        log.info(f"Listings before filtering: {len(listings)}")
        result = [listing for listing in listings if self.matches(listing)]
        log.info(f"Listings after filtering: {len(result)}")
        return result
