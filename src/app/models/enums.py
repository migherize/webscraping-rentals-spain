from __future__ import annotations
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class URLs(str, Enum):
    flipcoliving = "https://flipcoliving.com/"
    somosalthena = "https://somosalthena.com/"
    nodis = "https://nodis.es/"


class ScrapinBeeParams(str, Enum):
    RENDER_JS = "render_js"
    EXTRACT_RULES = "extract_rules"


# Internal lodgerin
class Description(BaseModel):
    LanguagesId: int
    title: str
    description: str


class Image(BaseModel):
    image: str
    isCover: bool


class Location(BaseModel):
    lat: str
    lon: str
    address: str
    fullAddress: str
    number: str
    country: str
    countryCode: str
    state: str
    city: str
    street: str
    postalCode: str
    prefixPhone: str


class Model(BaseModel):
    oldId: Optional[int] = None
    userOldId: Optional[int] = None
    name: Optional[str] = None
    description: Optional[str] = None
    referenceCode: Optional[str] = None
    PropertyTypeId: Optional[int] = None
    provider: Optional[str] = None
    providerId: Optional[int] = None
    providerRef: Optional[str] = None
    cancellationPolicy: Optional[str] = None
    maxOccupancy: Optional[int] = None
    minAge: Optional[int] = None
    maxAge: Optional[int] = None
    rentalType: Optional[str] = None
    tenantGender: Optional[str] = None
    PensionTypeId: Optional[int] = None
    videoUrl: Optional[str] = None
    tourUrl: Optional[str] = None
    isActive: Optional[bool] = None
    isPublished: Optional[bool] = None
    Descriptions: Optional[List[Description]] = None
    Features: Optional[List[int]] = None
    Images: Optional[List[Image]] = None
    Languages: Optional[List[int]] = None
    Location: Optional[Location] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
