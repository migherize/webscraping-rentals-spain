from __future__ import annotations
from enum import Enum
from pydantic import BaseModel
from typing import List, Optional

class URLs(str, Enum):
    flipcoliving = "https://flipcoliving.com/"
    somosalthena = "https://somosalthena.com/"
    nodis = "https://nodis.es/"


class ScrapingBeeParams(str, Enum):
    RENDER_JS = "render_js"
    EXTRACT_RULES = "extract_rules"

class Month(Enum):
    JANUARY = 1
    FEBRUARY = 2
    MARCH = 3
    APRIL = 4
    MAY = 5
    JUNE = 6
    JULY = 7
    AUGUST = 8
    SEPTEMBER = 9
    OCTOBER = 10
    NOVEMBER = 11
    DECEMBER = 12
    ENERO = 1
    FEBRERO = 2
    MARZO = 3
    ABRIL = 4
    MAYO = 5
    JUNIO = 6
    JULIO = 7
    AGOSTO = 8
    SEPTIEMBRE = 9
    OCTUBRE = 10
    NOVIEMBRE = 11
    DICIEMBRE = 12

feature_map = {
    "1": ["air conditioning", "aire acondicionado"],
    "2": ["bed linen", "ropa de cama", "sábanas"],
    "3": ["census", "registro en el censo", "inscripción censal"],
    "4": ["cleaning common areas", "limpieza de áreas comunes"],
    "5": ["common areas", "áreas comunes"],
    "6": ["electricity", "electricidad"],
    "7": ["exterior", "exterior", "ventanas exteriores"],
    "8": ["fully managed", "totalmente gestionado"],
    "9": ["guests night allowed", "se permiten noches de invitados"],
    "10": ["heating system", "sistema de calefacción"],
    "11": ["instant booking", "reserva instantánea"],
    "12": ["internet", "internet", "wi-fi"],
    "13": ["lift", "ascensor", "elevador"],
    "14": ["lockable door", "puerta con cerradura"],
    "15": ["mailbox access", "acceso a buzón"],
    "16": ["maintenance", "mantenimiento"],
    "17": ["pets allowed", "se permiten mascotas"],
    "18": ["private balcony/terrace", "balcón/terraza privado"],
    "19": ["private bath", "baño privado"],
    "20": ["smoking allowed", "se permite fumar"],
    "21": ["study area (Chair & table)", "zona de estudio (silla y mesa)"],
    "22": ["swimming pool", "piscina"],
    "23": ["terrace / balcony", "terraza / balcón"],
    "24": ["water", "agua"],
    "25": ["24hr Concierge Reception", "recepción 24 horas"],
    "26": ["shared bath", "baño compartido"],
    "27": ["bathroom", "baño", "cuarto de baño"],
    "28": ["bedroom lock", "cerradura de habitación"],
    "29": ["bicycle parking", "aparcamientos de bicicletas"],
    "30": ["car parking", "aparcamientos de coches"],
    "31": ["elevator", "ascensor"],
    "32": ["furnished", "amueblado"],
    "33": ["extra storage", "almacenamiento extra"],
    "34": ["game room", "sala de juegos"],
    "35": ["smoke alarm", "alarma de humo"],
    "36": ["shared study area", "zona de estudio compartida"],
    "37": ["shower", "ducha"],
    "38": ["sports facilities", "instalaciones deportivas"],
    "39": ["towels", "toallas"],
    "40": ["video surveillance", "videovigilancia"],
    "41": ["visually impaired access", "acceso para personas con discapacidad visual"],
    "42": ["wheelchair access", "acceso para sillas de ruedas"],
    "43": ["wi-fi", "wi-fi", "internet inalámbrico"],
    "44": ["playing music", "reproducción de música"],
    "45": ["couples", "parejas"],
}




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
