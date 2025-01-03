from typing import Dict, List, Optional

from pydantic import BaseModel, Field


class Description(BaseModel):
    LanguagesId: int = Field(
        ..., description="ID del idioma. Valores: 1 = Español, 2 = Inglés."
    )
    title: str = Field(
        ..., description="Título de la propiedad en el idioma seleccionado."
    )
    description: str = Field(
        ..., description="Descripción de la propiedad en el idioma seleccionado."
    )


class Image(BaseModel):
    image: str = Field(..., description="URL o Base64 de la imagen.")
    isCover: bool = Field(
        ..., description="Indica si la imagen es portada / principal."
    )


class LocationAddress(BaseModel):
    number: Optional[str] = Field(None, description="Número de la dirección.")
    lat: Optional[str] = Field(None, description="Latitud de la dirección.")
    lon: Optional[str] = Field(None, description="Longitud de la dirección.")
    fullAddress: Optional[str] = Field(
        None, description="Dirección completa de la dirección."
    )
    address: Optional[str] = Field(None, description="Dirección de la dirección.")
    city: Optional[str] = Field(None, description="Ciudad de la dirección.")
    street: Optional[str] = Field(
        None, description="Calle/Avenida/Sector/Barrio de la ubicación."
    )
    state: Optional[str] = Field(None, description="Estado de la dirección.")
    postalCode: Optional[str] = Field(
        None, description="Código postal de la dirección."
    )
    country: Optional[str] = Field(None, description="País de la dirección.")
    countryCode: Optional[str] = Field(
        None, description="Código de país de la dirección."
    )
    prefixPhone: Optional[str] = Field(None, description="Código telefónico del país.")

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


class Property(BaseModel):
    id: Optional[str] = Field(None, description="ID de la propiedad.")
    name: Optional[str] = Field(None, description="Nombre/etiqueta de la propiedad.")
    description: Optional[str] = Field(None, description="Descripción de la propiedad.")
    referenceCode: str = Field(
        ..., min_length=3, description="Código de referencia (min: 3 caracteres)."
    )
    minAge: Optional[int] = Field(
        None, description="Edad mínima permitida de los inquilinos."
    )
    maxAge: Optional[int] = Field(
        None, description="Edad máxima permitida de los inquilinos."
    )
    areaM2: Optional[int] = Field(None, description="Área (en metros) de la propiedad.")
    areaM2Available: Optional[int] = Field(
        None, description="Área disponible (en metros) de la propiedad."
    )
    maxOccupancy: Optional[int] = Field(
        None, description="Aforo máximo de la propiedad."
    )
    dateLastReform: Optional[str] = Field(
        None,
        description="Fecha de la última reforma de la propiedad (formato: YYYY-MM-DD).",
    )
    tenantGender: Optional[str] = Field(
        None,
        description="Género de los arrendatarios permitidos en la propiedad.",
    )
    cancellationPolicy: Optional[str] = Field(
        None,
        description="Política de cancelación para los arrendatarios en la propiedad.",
    )
    rentalType: Optional[str] = Field(
        None,
        description="Tipo de alquiler de la propiedad.",
    )
    isActive: Optional[bool] = Field(
        None, description="Indica si la propiedad se encuentra activa para su gestión."
    )
    isPublished: Optional[bool] = Field(
        None,
        description="Indica si la propiedad se encuentra publicada para su gestión.",
    )

    Features: Optional[List[int]] = Field(
        None, description="IDs de las características a asociar en la propiedad."
    )
    Languages: Optional[List[int]] = Field(
        None, description="IDs de los idiomas a asociar en la propiedad."
    )

    videoUrl: Optional[str] = Field(None, description="URL del video de la propiedad.")
    tourUrl: Optional[str] = Field(
        None, description="URL del tour virtual de la propiedad."
    )

    PropertyTypeId: Optional[int] = Field(None, description="ID del tipo de propiedad.")
    PensionTypeId: Optional[int] = Field(None, description="ID del tipo de pensión.")

    Descriptions: Optional[List["Description"]] = Field(
        [], description="Listado de títulos y descripciones."
    )
    Images: Optional[List["Image"]] = Field(
        [], description="Listado de imágenes de la propiedad."
    )

    Location: Optional["LocationAddress"] = Field(
        None, description="Información de la ubicación de la propiedad."
    )
    provider: Optional[str] = Field(None, description="ID de la provider.")
    providerRef: Optional[str] = Field(None, description="ID de la providerRef.")


class Extra(BaseModel):
    name: str = Field(..., description="Etiqueta del precio extra.")
    currency: str = Field(..., description="Código de moneda.")
    amount: int = Field(..., description="Monto del precio extra.")


class ContractModel(BaseModel):
    PropertyBusinessModelId: int = Field(
        ..., description="ID del modelo de contratación."
    )
    currency: str = Field(
        ..., description="Código de moneda. Ejemplo: 'EUR', 'USD', ..."
    )
    amount: int = Field(..., description="Monto de alquiler.")
    depositAmount: int = Field(..., description="Monto de depósito.")
    reservationAmount: int = Field(..., description="Monto de reserva.")
    minPeriod: int = Field(..., description="Mínimo de periodo de reservación.")
    paymentCycle: str = Field(
        ...,
        description="Ciclo de pago modalidades.",
    )
    extras: List[Extra] = Field([], description="Listado de precios extras.")


class RentalUnits(BaseModel):
    id: Optional[str] = Field(None, description="ID de la rental unit.")
    PropertyId: str = Field(
        ..., description="ID de la propiedad a la que pertenece la rental unit"
    )
    referenceCode: str = Field(
        ..., min_length=3, description="Código de referencia de la rental unit"
    )
    areaM2: Optional[int] = Field(
        None, description="Área total de la rental unit en metros cuadrados."
    )
    areaM2Available: Optional[int] = Field(
        None, description="Área disponible de la rental unit en metros cuadrados."
    )
    maxCapacity: Optional[str] = Field(
        None, description="Capacidad máxima (número de personas) en la rental unit."
    )
    urlICalSync: Optional[str] = Field(
        None, description="URL de sincronización iCal de la rental unit."
    )
    bedType: Optional[str] = Field(
        None,
        description="Tipo de cama. Valores posibles: 'individual', 'double', 'queen', 'king'.",
    )
    Features: Optional[List[int]] = Field(
        default_factory=list,
        description="Lista de IDs de características asociadas a la rental unit.",
    )
    Furnitures: Optional[List[int]] = Field(
        default_factory=list,
        description="Lista de IDs de mobiliario asociados a la rental unit.",
    )
    isActive: Optional[bool] = Field(
        None, description="Indica si la rental unit está activa o archivada."
    )
    isPublished: Optional[bool] = Field(
        None,
        description="Indica si la rental unit está publicada y visible para los usuarios.",
    )
    ContractsModels: List[ContractModel] = Field(
        default_factory=list,
        description="Lista de modelos de contratación asociados a la rental unit.",
    )
    Descriptions: Optional[List[Description]] = Field(
        [], description="Listado de títulos y descripciones."
    )
    Images: Optional[List[Image]] = Field(
        [], description="Listado de imágenes de la propiedad."
    )


class DatePayloadItem(BaseModel):
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


# Elements
class DatePayload(BaseModel):
    dates: List[DatePayloadItem]


class ContractTypeItem(BaseModel):
    id: int
    name: str
    description: Optional[str]


class ContractTypes(BaseModel):
    data: List[ContractTypeItem]


class SpaceTypeItem(BaseModel):
    id: int
    name: str
    description: str
    type: str
    icon: Optional[str]
    canBeRentalUnit: bool


class SpacesTypes(BaseModel):
    data: List[SpaceTypeItem]


class PropertyTypeItem(BaseModel):
    id: int
    name: str
    description: str


class PropertyTypes(BaseModel):
    data: List[PropertyTypeItem]


class RentalUnitTypeItem(BaseModel):
    id: int
    name: str
    description: str


class RentalUnitsTypes(BaseModel):
    data: List[RentalUnitTypeItem]


class FeatureItem(BaseModel):
    id: int
    name: str
    description: str
    icon: Optional[str]


class Features(BaseModel):
    data: List[FeatureItem]


class FurnitureItem(BaseModel):
    id: int
    name: str
    description: str
    icon: Optional[str]


class Furnitures(BaseModel):
    data: List[FurnitureItem]


class LanguageItem(BaseModel):
    id: int
    name_es: str
    name_en: str
    code: str


class Languages(BaseModel):
    data: List[LanguageItem]


class PensionTypeItem(BaseModel):
    id: int
    name: Optional[str]


class PensionTypes(BaseModel):
    data: List[PensionTypeItem]


class ApiKeyItem(BaseModel):
    id: str
    name: str
    location: Optional[str]


class ApiKey(BaseModel):
    data: List[ApiKeyItem]


mapping = {
    "contract_types": ContractTypes,
    "spaces_types": SpacesTypes,
    "property_types": PropertyTypes,
    "rental_units_types": RentalUnitsTypes,
    "features": Features,
    "furnitures": Furnitures,
    "languages": Languages,
    "pension_types": PensionTypes,
    "api_key": ApiKey,
}
