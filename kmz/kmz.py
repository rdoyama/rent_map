import json
import logging
from typing import Any, List

import simplekml
from pydantic import TypeAdapter
from simplekml import Style

from misc.color import Color, ColorInterpolation
from model.MarketModel import MarketModel
from model.listing_model import Listing

logger = logging.getLogger(__name__)


class KMZ:
    def __init__(self, utilities: Any, destination: str = 'rentMap.kmz'):
        self.destination = destination
        self.kml = simplekml.Kml(open=1, name='RentMap')
        self.utilities = utilities
        self.base_url = ''
        self._set_styles()

    def set_base_url(self, base_url: str):
        self.base_url = base_url

    def _set_styles(self):
        self.star_icon = 'http://maps.google.com/mapfiles/kml/paddle/ylw-stars.png'
        self.generic_pin = self.kml.addfile('resources/blank-pin.png')
        self.grocery_icon = self.kml.addfile('resources/grocery_2.png')

    def process_listings(self, listings: list[Listing]):
        listing_color_start = Color(204, 255, 204)
        listing_color_end = Color(0, 115, 0)
        prices = list(map(lambda l: l.listing.get_total_price() ,listings))
        val_min = min(prices)
        val_max = max(prices)
        ci = ColorInterpolation(listing_color_start, listing_color_end, val_min, val_max)
        for listing in listings:
            address_point = listing.get_address_point()
            if address_point is None:
                error_message = f"Address Point {address_point} not found. Program will continue"
                logger.warning(error_message)
                continue
            lat, lon = address_point.get_lat_lon()

            general_description = listing.listing.description
            pricing_description = listing.listing.get_rental_pricing_info()
            if pricing_description is None:
                logger.info(f"Listing with href {listing.link.href} does not have rent price")
                continue
            pricing_description = pricing_description.get_pricing_description()
            contact_info = listing.get_contact_info()
            description = pricing_description + '<br><br>' + contact_info + '<br><br>' + general_description
            if listing.listing.address.point.is_address_approximated():
                description = self.get_approximated_address_warn(listing.listing.address.get_address()) + '<br><br>' + description
            href = listing.link.href

            if self.is_price_below_average(listing):
                self.populate_kml(lat, lon, description, href, icon=self.star_icon)
            else:
                price = listing.listing.get_total_price()
                icon_color = ci.interpolate(price).to_kml_hex()
                self.populate_kml(lat, lon, description, href, icon=self.generic_pin, icon_color=icon_color)

    def populate_kml(self, lat: float, lon: float, description: str | None, href: str | None, title: str | None = '',
                     icon: str = None, icon_color: str = None, icon_scale: float = 1.0, label_scale: float = 0.8):
        if href is None:
            url = ""
        else:
            url = f'<a href="{self.base_url + href}">Link do anúncio</a>'
        full_description = url
        if description is not None:
            full_description += '<br><br>' + description
        point = self.kml.newpoint(name = title, coords = [(lon, lat)], description = full_description)
        if icon is not None:
            point.iconstyle.icon.href = icon
            if icon_color is not None:
                point.iconstyle.color = icon_color
        point.iconstyle.scale = icon_scale
        point.style.labelstyle.scale = label_scale

    def generate_kmz(self):
        self.kml.savekmz(self.destination)
        logger.info(f'KMZ file {self.destination} generated')

    @staticmethod
    def get_approximated_address_warn(address: str) -> str:
        return f'!!! Esta é uma localização aproximada para {address} !!!'

    @staticmethod
    def get_markets_from_json(path: str = 'resources/markets.json'):
        with open(path, 'r', encoding='utf-8') as file:
            market_data = json.load(file)
        type_adapter = TypeAdapter(List[MarketModel])
        return type_adapter.validate_python(market_data)

    def add_utilities(self):
        add_markets = True if self.utilities['add_markets'] == 'True' else False
        if add_markets:
            for market in self.get_markets_from_json():
                self.populate_kml(market.lat, market.lon, None, None, market.name, self.grocery_icon,
                                  market.icon_color, market.icon_scale, market.label_scale)

    @staticmethod
    def is_price_below_average(listing: Listing) -> bool:
        return 'DATAZAP_APPROVED_RENTAL' in listing.listing.stamps
