import logging
from typing import Any

import simplekml

from custom_requests.zap_listing_model import ZapListing, AddressPoint

logger = logging.getLogger(__name__)


class KMZ:
    def __init__(self, listings: list[ZapListing], config: Any, destination: str = 'rentMap.kmz'):
        self.listings = listings
        self.destination = destination
        self.kml = simplekml.Kml(open=1, name='RentMap')
        self.base_url = config['base_url']

    def process_listings(self):
        for listing in self.listings:
            address_point = self.get_address_point(listing)
            if address_point is None:
                error_message = f"Address Point {address_point} not found. Program will continue"
                logger.warning(error_message)
                continue
            lat, lon = self.get_lat_lon(address_point)

            general_description = listing.listing.description
            pricing_description = self.get_pricing_description(listing)
            contact_info = self.get_contact_info(listing)
            description = pricing_description + '<br><br>' + contact_info + '<br><br>' + general_description
            if self.is_address_approximated(listing):
                description = self.get_approximated_address_warn(listing) + '<br><br>' + description
            href = listing.link.href

            self.populate_kml(lat, lon, description, href)
        self.generate_kmz()

    @staticmethod
    def get_contact_info(listing: ZapListing):
        name = listing.account.name
        phone = listing.listing.whatsappNumber
        return f'Contato: {name}<br>Telefone/Celular: {phone}'

    @staticmethod
    def get_pricing_description(listing: ZapListing) -> str:
        yearly_iptu = listing.listing.pricingInfos[0].yearlyIptu
        price = listing.listing.pricingInfos[0].price
        monthly_condo_fee = listing.listing.pricingInfos[0].monthlyCondoFee
        return f"Aluguel: R${price:.2f}<br>Condomínio: R${monthly_condo_fee:.2f}<br>IPTU: R${yearly_iptu:.2f}"

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
    def get_address_point(listing: ZapListing) -> AddressPoint | None:
        listing_obj = listing.listing
        if listing_obj is None:
            return None
        address = listing_obj.address
        if address is None:
            return None
        if address.point is not None:
            return address.point
        return None

    @staticmethod
    def get_lat_lon(address_point: AddressPoint) -> tuple[float, float]:
        if address_point.lat == 0 or address_point.lon == 0:
            return address_point.approximateLat, address_point.approximateLon
        return address_point.lat, address_point.lon

    @staticmethod
    def is_address_approximated(listing: ZapListing) -> bool:
        address_point = listing.listing.address.point
        return address_point.lat == 0 or address_point.lon == 0 and address_point.approximateLat != 0 and address_point.approximateLon != 0

    @staticmethod
    def get_approximated_address_warn(listing: ZapListing) -> str:
        street = listing.listing.address.street
        neighborhood = listing.listing.address.neighborhood
        city = listing.listing.address.city
        stateAcronym = listing.listing.address.stateAcronym
        address = f'{street}, {neighborhood}, {city}/{stateAcronym}'
        return f'!!! Esta é uma localização aproximada para {address} !!!'