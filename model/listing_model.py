from datetime import datetime
from typing import Optional

from pydantic import ConfigDict
from pydantic.dataclasses import dataclass


@dataclass
class RentalInfo:
    period: Optional[str] = "Not specified"
    warranties: Optional[list[str]] = ()


@dataclass(config=ConfigDict(extra='ignore'))
class PricingInfo:
    rentalInfo: Optional[RentalInfo] = None
    businessType: str = "Not defined"
    price: float = 0
    monthlyCondoFee: float = 0
    yearlyIptu: float = 0
    monthlyRentalTotalPrice: float = 0

    def get_pricing_description(self):
        return f"Aluguel: R${self.price:.2f}<br>Condomínio: R${self.monthlyCondoFee:.2f}<br>IPTU: R${self.yearlyIptu:.2f}"


@dataclass(config=ConfigDict(extra='ignore'))
class AdvertiserContact:
    phones: list[str] = ()


@dataclass(config=ConfigDict(extra='ignore'))
class AddressPoint:
    lat: float = 0
    lon: float = 0
    approximateLat: float = 0
    approximateLon: float = 0
    source: str = "No sources"

    def is_address_approximated(self):
        return self.lat == 0 or self.lon == 0 and self.approximateLat != 0 and self.approximateLon != 0

    def get_lat_lon(self):
        if self.lat == 0 or self.lon == 0:
            return self.approximateLat, self.approximateLon
        return self.lat, self.lon


@dataclass(config=ConfigDict(extra='ignore'))
class Address:
    point: Optional[AddressPoint] = None
    city: str = "Not informed"
    neighborhood: str = "Not informed"
    street: str = "Not informed"
    streetNumber: str = "Not informed"
    stateAcronym: str = "Not informed"

    def get_address(self):
        if self.point.is_address_approximated():
            return f'{self.street}, {self.neighborhood}, {self.city}/{self.stateAcronym}'
        else:
            return f'{self.street} {self.streetNumber}, {self.neighborhood}, {self.city}/{self.stateAcronym}'


@dataclass(config=ConfigDict(extra='ignore'))
class ListingModel:
    updatedAt: Optional[datetime] = None
    address: Optional[Address] = None
    contractType: str = "Not informed"
    amenities: list[str] = ()
    usableAreas: list[int] = ()
    description: str = "Not informed"
    title: str = "Not informed"
    createdAt: str = "Not informed"
    floors: list[int] = ()
    unitTypes: list[str] = ()
    parkingSpaces: list[int] = ()
    suites: list[int] = ()
    bathrooms: list[int] = ()
    usageTypes: list[str] = ()
    whatsappNumber: str = "Not informed"
    bedrooms: list[int] = ()
    pricingInfos: list[PricingInfo] = ()

    def get_rental_pricing_info(self) -> PricingInfo:
        return list(filter(lambda p: p.businessType == 'RENTAL', self.pricingInfos))[0]


@dataclass(config=ConfigDict(extra='ignore'))
class Link:
    href: str = "Not informed"


@dataclass(config=ConfigDict(extra='ignore'))
class Account:
    name: str = "Not informed"
    licenseNumber: str = "Not informed"


@dataclass(config=ConfigDict(extra='ignore'))
class Listing:
    listing: Optional[ListingModel] = None
    link: Optional[Link] = None
    account: Optional[Account] = None

    def get_address_point(self) -> AddressPoint | None:
        listing_obj = self.listing
        if listing_obj is None:
            return None
        address = listing_obj.address
        if address is None:
            return None
        if address.point is not None:
            return address.point
        return None

    def get_contact_info(self):
        name = self.account.name
        phone = self.listing.whatsappNumber
        return f'Contato: {name}<br>Telefone/Celular: {phone}'

    @staticmethod
    def get_csv_headers(separator: str = ';') -> str:
        return separator.join([
            'Título',
            'Endereço',
            'Área',
            'Contato',
            'Aluguel',
            'Condomínio',
            'IPTU',
            'Link',
        ])

    def get_csv_line(self, base_url: str, separator: str = ';'):
        return separator.join([
            self.listing.title,
            self.listing.address.get_address(),
            str(self.listing.usableAreas[0]),
            self.get_contact_info(),
            str(int(self.listing.get_rental_pricing_info().price)),
            str(int(self.listing.get_rental_pricing_info().monthlyCondoFee)),
            str(int(self.listing.get_rental_pricing_info().yearlyIptu)),
            base_url + self.link.href
        ])
