from pydantic import BaseModel, HttpUrl, Field
from typing import List, Optional, Union


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


class Property(BaseModel):
    id: Optional[str] = Field(None, description="ID de la propiedad.")
    name: str = Field(..., description="Nombre/etiqueta de la propiedad.")
    description: str = Field(..., description="Descripción de la propiedad.")
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
        description="Género de los arrendatarios permitidos en la propiedad. Valores: indifferent = Indiferente, male = Hombres, female = Mujeres, other = Otros.",
    )
    cancellationPolicy: Optional[str] = Field(
        None,
        description="Política de cancelación para los arrendatarios en la propiedad. Valores: flexible = Flexible, standard = Estándar, strict = Estricto.",
    )
    rentalType: Optional[str] = Field(
        None,
        description="Tipo de alquiler de la propiedad. Valores: complete = Alquiler completo de la propiedad, individual = Alquiler por habitaciones.",
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


# class Extra(BaseModel):
#     name: str = Field(..., description="Etiqueta del precio extra.")
#     currency: str = Field(..., description="Código de moneda.")
#     amount: float = Field(..., description="Monto del precio extra.")


# class ContractModel(BaseModel):
#     PropertyBusinessModelId: int = Field(
#         ..., description="ID del modelo de contratación."
#     )
#     currency: str = Field(
#         ..., description="Código de moneda. Ejemplo: 'EUR', 'USD', ..."
#     )
#     amount: float = Field(..., description="Monto de alquiler.")
#     depositAmount: float = Field(..., description="Monto de depósito.")
#     reservationAmount: float = Field(..., description="Monto de reserva.")
#     minPeriod: int = Field(..., description="Mínimo de periodo de reservación.")
#     paymentCycle: str = Field(
#         ...,
#         description="Ciclo de pago modalidades. Valores: unknown = Diario, daily = Diario, fortnightly = Quincenal, monthly = Mensual.",
#     )
#     extras: Optional[List[Extra]] = Field([], description="Listado de precios extras.")


# class RentalUnits(BaseModel):
#     oldId: int = Field(..., description="ID de la rental unit en Legacy.")
#     oldPropertyId: int = Field(..., description="ID de la propiedad en Legacy.")
#     SpaceId: Optional[str] = Field(
#         None, description="ID (de arrento) del espacio a asociar a la rental unit."
#     )
#     referenceCode: str = Field(
#         ..., min_length=3, description="Código de referencia (min: 3 caracteres)."
#     )
#     urlICalSync: Optional[str] = Field(..., description="URL iCal de la rental unit.")

#     bedType: str = Field(
#         ...,
#         description="Tipo de cama. Valores: individual = Cama individual, double = Cama doble, queen = Cama queen, king = Cama rey.",
#     )

#     isActive: Optional[bool] = Field(
#         ..., description="Indica si la rental unit se encuentra activa para su gestión."
#     )
#     isPublished: Optional[bool] = Field(
#         ..., description="Indica si la rental unit se publicada a los usuarios."
#     )

#     Features: List[int] = Field(
#         ..., description="Listado de características asociadas."
#     )
#     Furnitures: List[int] = Field(..., description="Listado de mobiliario asociadas.")

#     # Campo añadido para la capacidad máxima
#     maxCapacity: int = Field(
#         ..., description="Capacidad máxima de la unidad de alquiler."
#     )

#     createdAt: Optional[str] = Field(
#         ...,
#         description="Fecha de creación de la rental unit en la base de datos Legacy.",
#     )
#     updatedAt: Optional[str] = Field(
#         ...,
#         description="Fecha de la última actualización de la rental unit en la base de datos Legacy.",
#     )

#     ContractsModels: List[ContractModel] = Field(
#         ..., description="Listado de modelos de contratación asociados."
#     )
#     Descriptions: Optional[List[Description]] = Field(
#         [], description="Listado de títulos y descripciones."
#     )
#     Images: Optional[List[Image]] = Field(
#         [], description="Listado de imágenes de la rental unit."
#     )
