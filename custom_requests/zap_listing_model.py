from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pydantic import BaseModel


dataclass_config = {
    'init': False,
    'repr': False,
    'eq': False,
    'order': False,
    'match_args': False,
}


@dataclass(**dataclass_config)
class RentalInfo(BaseModel):
    period: Optional[str] = "Not specified"
    warranties: Optional[list[str]] = None


@dataclass(**dataclass_config)
class PricingInfo(BaseModel):
    businessType: Optional[str] = "Not defined"
    price: Optional[float] = 0
    monthlyCondoFee: Optional[float] = 0
    rentalInfo: Optional[RentalInfo] = None
    yearlyIptu: Optional[float] = 0
    monthlyRentalTotalPrice: Optional[float] = None


@dataclass(**dataclass_config)
class AdvertiserContact(BaseModel):
    phones: Optional[list[str]] = None


@dataclass(**dataclass_config)
class AddressPoint(BaseModel):
    lat: Optional[float] = 0
    lon: Optional[float] = 0
    approximateLat: Optional[float] = 0
    approximateLon: Optional[float] = 0
    source: Optional[str] = "No sources"


@dataclass(**dataclass_config)
class Address(BaseModel):
    city: Optional[str] = "Not informed"
    neighborhood: Optional[str] = "Not informed"
    street: Optional[str] = "Not informed"
    streetNumber: Optional[str] = "Not informed"
    point: Optional[AddressPoint] = None
    stateAcronym: Optional[str] = "Not informed"


@dataclass(**dataclass_config)
class ZapListingModel(BaseModel):
    contractType: Optional[str] = "Not informed"
    amenities: Optional[list[str]] = None
    description: Optional[str] = "Not informed"
    title: Optional[str] = "Not informed"
    createdAt: Optional[str] = "Not informed"
    floors: Optional[list[int]] = None
    unitTypes: Optional[list[str]] = None
    parkingSpaces: Optional[list[int]] = None
    updatedAt: Optional[datetime] = None
    address: Optional[Address] = None
    suites: Optional[list[int]] = None
    bathrooms: Optional[list[int]] = None
    usageTypes: Optional[list[str]] = None
    whatsappNumber: Optional[str] = "Not informed"
    bedrooms: Optional[list[int]] = None
    pricingInfos: Optional[list[PricingInfo]] = None


@dataclass(**dataclass_config)
class Link(BaseModel):
    href: Optional[str] = "Not informed"


@dataclass(**dataclass_config)
class Account(BaseModel):
    name: Optional[str] = "Not informed"
    licenseNumber: Optional[str] = "Not informed"


@dataclass(**dataclass_config)
class ZapListing(BaseModel):
    listing: Optional[ZapListingModel] = None
    link: Optional[Link] = None
    account: Optional[Account] = None


