from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class CounterRU(BaseModel):
    occupiedRUs: Optional[int] = Field(..., description="")
    totalRUs: Optional[int] = Field(..., description="")


class Feature(BaseModel):
    id: Optional[int] = Field(..., description="")
    label: Optional[str] = Field(..., description="")
    icon: Optional[str] = Field(..., description="")
    group: Optional[List[str]] = Field(..., description="")
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
    lat: Optional[str] = Field(None, description="Latitud de la dirección.")
    lon: Optional[str] = Field(None, description="Longitud de la dirección.")


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
    areaM2Available: Optional[str] = Field(None, description="")
    dateLastReform: Optional[str] = Field(None, description="")
    numBathrooms: Optional[str] = Field(None, description="")


class RentalUnits(BaseModel):
    Images: Optional[List["Image"]] = Field(None, description="")
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


class RentalUnitsCalendarItem(BaseModel):
    summary: str = Field(
        ...,
        description="Short summary for the date range, e.g., 'Blocked until August 2025'",
    )
    description: str = Field(
        ...,
        description="Detailed description of availability, e.g., 'Available from August 2025'",
    )
    startDate: str = Field(..., description="Start date of the blocked range")
    endDate: str = Field(..., description="End date of the blocked range")


class RentalUnitsCalendar(BaseModel):
    dates: List[RentalUnitsCalendarItem]




########## MODELOS GENERALES  ########## 
class LocationMaps(BaseModel):
    boundingbox: Optional[List[float]] = Field(None, description="Caja delimitadora de la ubicación (latitudes y longitudes).")
    lat: Optional[float] = Field(None, description="Latitud de la dirección.")
    lon: Optional[float] = Field(None, description="Longitud de la dirección.")
    address: Optional[str] = Field(None, description="Dirección de la ubicación.")
    fullAddress: Optional[str] = Field(None, description="Dirección completa de la ubicación.")
    number: Optional[str] = Field(None, description="Número de la dirección.")
    country: Optional[str] = Field(None, description="País de la dirección.")
    countryCode: Optional[str] = Field(None, description="Código de país de la dirección.")
    state: Optional[str] = Field(None, description="Estado de la dirección.")
    city: Optional[str] = Field(None, description="Ciudad de la dirección.")
    street: Optional[str] = Field(None, description="Calle o avenida de la dirección.")
    postalCode: Optional[str] = Field(None, description="Código postal de la dirección.")
    prefixPhone: Optional[str] = Field(None, description="Prefijo telefónico del país.")

########### ###################### ###########


class ContractsModelsItem(BaseModel):
    id: int
    label: str
    name_es: str
    name_en: str


class ContractsModels(BaseModel):
    data: List[ContractsModelsItem]


class FeatureItem(BaseModel):
    id: int
    label: str
    icon:  Optional[str]
    group: Optional[List[str]]
    name_es: Optional[str]
    name_en: Optional[str]


class Features(BaseModel):
    data: List[FeatureItem]


class KitchenItem(BaseModel):
    id: int
    label: str
    icon:  Optional[str]
    name_es: Optional[str]
    name_en: Optional[str]


class Kitchen(BaseModel):
    data: List[KitchenItem]


class LanguageItem(BaseModel):
    id: int
    name_es: str
    name_en: str
    code: str


class Languages(BaseModel):
    data: List[LanguageItem]


class PropertyTypeItem(BaseModel):
    id: int
    label: str
    name_es: str
    name_en: str
    totalProperties: int
    totalRentalUnits: int


class PropertyTypes(BaseModel):
    data: List[PropertyTypeItem]


class RentalConditionsItem(BaseModel):
    id: int
    label: str
    icon: Optional[str]
    name_es: str
    name_en: str


class RentalConditions(BaseModel):
    data: List[RentalConditionsItem]


class RentalUnitsStatesItem(BaseModel):
    id: int
    label: str
    canBeACost: bool
    name_es: str
    name_en: str


class RentalUnitsStates(BaseModel):
    data: List[RentalUnitsStatesItem]


class ServicesItem(BaseModel):
    id: int
    label: str
    icon: Optional[str]
    name_es: str
    name_en: str


class Services(BaseModel):
    data: List[ServicesItem]


class ApiKeyItem(BaseModel):
    id: str
    name: str
    location: Optional[str]


class ApiKey(BaseModel):
    data: List[ApiKeyItem]


mapping = {
    "contractsModels": ContractsModels,
    "features": Features,
    "kitchen": Kitchen,
    "languages": Languages,
    "propertiesTypes": PropertyTypes,
    "rentalConditions": RentalConditions,
    "rentalUnitsStates": RentalUnitsStates,
    "services": Services,
    "api_key": ApiKey,
}
