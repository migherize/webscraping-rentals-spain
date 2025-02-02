from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class Property(BaseModel):
    CountersRU: Optional["CounterRU"] = Field(None, description="")
    Features: Optional[List["Feature"]] = Field(None, description="")
    Images: Optional[List["Image"]] = Field(None, description="")
    Location: Optional["LocationAddress"] = Field(None, description="")
    PropertyType: Optional["PropertyTypeModel"] = Field(None, description="")
    Texts: Optional["Text"] = Field(None, description="")
    areaM2: Optional[int] = Field(None, description="")
    code: Optional[str] = Field(None, description="")
    createdAt: Optional[str] = Field(None, description="")
    id: Optional[str] = Field(None, description="")
    isActive: Optional[bool] = Field(None, description="")
    isEntirePropertyRental: Optional[bool] = Field(None, description="")
    isPublished: Optional[bool] = Field(None, description="")
    maxOccupancy: Optional[int] = Field(None, description="")
    provider: Optional[str] = Field(None, description="")
    providerRef: Optional[str] = Field(None, description="")
    referenceCode: Optional[str] = Field(None, description="")
    rentalType: Optional[str] = Field(None, description="")
    typeSize: Optional[str] = Field(None, description="")
    updatedAt: Optional[str] = Field(None, description="")
    # TODO: Valores con None en el response
    areaM2Available: Optional[str] = Field(None, description="")
    dateLastReform: Optional[str] = Field(None, description="")
    numBathrooms: Optional[str] = Field(None, description="")


class CounterRU(BaseModel):
    occupiedRUs: Optional[int] = Field(..., description="")
    totalRUs: Optional[int] = Field(..., description="")


class Feature(BaseModel):
    group: Optional[list[str]] = Field(..., description="")
    icon: Optional[str] = Field(..., description="")
    id: Optional[int] = Field(..., description="")
    label: Optional[str] = Field(..., description="")
    name_en: Optional[str] = Field(..., description="")
    name_es: Optional[str] = Field(..., description="")


class Image(BaseModel):
    id: Optional[str] = Field(..., description="")
    image: Optional[str] = Field(..., description="URL o Base64 de la imagen.")
    isCover: Optional[bool] = Field(
        ..., description="Indica si la imagen es portada / principal."
    )


class LocationAddress(BaseModel):
    address: Optional[str] = Field(..., description="Dirección de la dirección.")
    city: Optional[str] = Field(..., description="Ciudad de la dirección.")
    country: Optional[str] = Field(..., description="País de la dirección.")
    countryCode: Optional[str] = Field(
        ..., description="Código de país de la dirección."
    )
    fullAddress: Optional[str] = Field(
        ..., description="Dirección completa de la dirección."
    )
    number: Optional[str] = Field(..., description="Número de la dirección.")
    postalCode: Optional[str] = Field(..., description="Código postal de la dirección.")
    prefixPhone: Optional[str] = Field(..., description="Código telefónico del país.")
    state: Optional[str] = Field(..., description="Estado de la dirección.")
    street: Optional[str] = Field(
        ..., description="Calle/Avenida/Sector/Barrio de la ubicación."
    )
    # TODO: Preguntar si aplican estos campos. En la data del response no aparece "lat" ni "log"
    # lat: Optional[str] = Field(None, description="Latitud de la dirección.")
    # lon: Optional[str] = Field(None, description="Longitud de la dirección.")


class PropertyTypeModel(BaseModel):
    id: Optional[int] = Field(..., description="")
    label: Optional[str] = Field(..., description="")
    name_en: Optional[str] = Field(..., description="")
    name_es: Optional[str] = Field(..., description="")


class Text(BaseModel):
    description_en: Optional[str] = Field(..., description="")
    description_es: Optional[str] = Field(..., description="")
    title_en: Optional[str] = Field(..., description="")
    title_es: Optional[str] = Field(..., description="")


class RentalUnits(BaseModel):
    Images: Optional["Image"] = Field(None, description="")
    Prices: Optional[List["Price"]] = Field(None, description="")
    Texts: Optional["Text"] = Field(None, description="")
    areaM2: Optional[int] = Field(None, description="")
    areaM2Available: Optional[int] = Field(None, description="")
    bedType: Optional[str] = Field(None, description="")
    code: Optional[str] = Field(None, description="")
    createdAt: Optional[str] = Field(None, description="")
    dateLastReform: Optional[str] = Field(None, description="")
    id: Optional[str] = Field(None, description="")
    isActive: Optional[bool] = Field(None, description="")
    isEnableCancellationPolicies: Optional[bool] = Field(None, description="")
    isPublished: Optional[bool] = Field(None, description="")
    level: Optional[str] = Field(None, description="")
    maxCapacity: Optional[str] = Field(None, description="")
    notes: Optional[str] = Field(None, description="")
    oldId: Optional[int] = Field(None, description="")
    propertyCode: Optional[str] = Field(None, description="")
    providerRef: Optional[str] = Field(None, description="")
    publicId: Optional[str] = Field(None, description="")
    referenceCode: Optional[str] = Field(None, description="")
    status: Optional[str] = Field(None, description="")
    typeSize: Optional[str] = Field(None, description="")
    updatedAt: Optional[str] = Field(None, description="")
    urlICalSync: Optional[str] = Field(None, description="")
    ExtraFeatures: Optional[List] = Field(None, description="")


class Price(BaseModel):
    amount: Optional[int] = Field(..., description="")
    contractType: Optional[str] = Field(..., description="")
    createdAt: Optional[str] = Field(..., description="")
    currency: Optional[str] = Field(..., description="")
    depositAmount: Optional[int] = Field(..., description="")
    discountPercent: Optional[int] = Field(..., description="")
    id: Optional[str] = Field(..., description="")
    maxPeriod: Optional[int] = Field(..., description="")
    minPeriod: Optional[int] = Field(..., description="")
    paymentCycle: Optional[str] = Field(..., description="")
    reservationAmount: Optional[int] = Field(..., description="")
    updatedAt: Optional[str] = Field(..., description="")
