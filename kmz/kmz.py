import logging
from typing import Any

import simplekml

from model.listing_model import Listing

logger = logging.getLogger(__name__)


class KMZ:
    def __init__(self, listings: list[Listing], config: Any, destination: str = 'rentMap.kmz'):
        self.listings = listings
        self.destination = destination
        self.kml = simplekml.Kml(open=1, name='RentMap')
        self.base_url = config['base_url']

    def process_listings(self):
        for listing in self.listings:
            address_point = listing.get_address_point()
            if address_point is None:
                error_message = f"Address Point {address_point} not found. Program will continue"
                logger.warning(error_message)
                continue
            lat, lon = address_point.get_lat_lon()

            general_description = listing.listing.description
            pricing_description = listing.listing.get_rental_pricing_info().get_pricing_description()
            contact_info = listing.get_contact_info()
            description = pricing_description + '<br><br>' + contact_info + '<br><br>' + general_description
            if listing.listing.address.point.is_address_approximated():
                description = self.get_approximated_address_warn(listing.listing.address.get_address()) + '<br><br>' + description
            href = listing.link.href

            self.populate_kml(lat, lon, description, href)
        self.generate_kmz()

    def populate_kml(self, lat: float, lon: float, description: str, href: str):
        if href is None:
            url = ""
        else:
            url = f'<a href="{self.base_url + href}">Link do anúncio</a>'
        full_description = url + '<br><br>' + description
        self.kml.newpoint(coords=[(lon, lat)], description=full_description)

    def generate_kmz(self):
        self.kml.savekmz(self.destination)
        logger.info(f'KMZ file {self.destination} generated')

    @staticmethod
    def get_approximated_address_warn(address: str) -> str:
        return f'!!! Esta é uma localização aproximada para {address} !!!'