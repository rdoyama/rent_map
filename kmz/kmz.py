import json
import logging
from typing import Any, List

import simplekml
from pydantic import TypeAdapter

from model.MarketModel import MarketModel
from model.listing_model import Listing

logger = logging.getLogger(__name__)


class KMZ:
    def __init__(self, listings: list[Listing], config: Any, utilities: Any, destination: str = 'rentMap.kmz'):
        self.listings = listings
        self.destination = destination
        self.kml = simplekml.Kml(open=1, name='RentMap')
        self.base_url = config['base_url']
        self.utilities = utilities

    def process_listings(self):
        for listing in self.listings:
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

            self.populate_kml(lat, lon, description, href, icon=listing.kml_icon, icon_color=listing.kml_icon_color)
        self.add_utilities()
        self.generate_kmz()

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
                logger.info(f'Checking Market name special chars: {market.name}')
                self.populate_kml(market.lat, market.lon, None, None, market.name, market.icon,
                                  market.icon_color, market.icon_scale, market.label_scale)
