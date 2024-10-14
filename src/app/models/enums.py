from __future__ import annotations
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel


class URLs(str, Enum):
    flipcoliving = "https://flipcoliving.com/"
    somosalthena = "https://somosalthena.com/"
    nodis = "https://nodis.es/"


class ScrapingBeeParams(str, Enum):
    RENDER_JS = "render_js"
    EXTRACT_RULES = "extract_rules"


# Internal lodgerin
class Description(BaseModel):
    LanguagesId: Optional[int] = None
    title: Optional[str] = None
    description: Optional[str] = None


class Image(BaseModel):
    image: Optional[str] = None
    isCover: Optional[bool] = None


class LocationAddress(BaseModel):
    lat: Optional[str] = None
    lon: Optional[str] = None
    address: Optional[str] = None
    fullAddress: Optional[str] = None
    number: Optional[str] = None
    country: Optional[str] = None
    countryCode: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    street: Optional[str] = None
    postalCode: Optional[str] = None
    prefixPhone: Optional[str] = None


class ModelInternalLodgerin(BaseModel):
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
    Location: Optional[LocationAddress] = None
    createdAt: Optional[str] = None
    updatedAt: Optional[str] = None
