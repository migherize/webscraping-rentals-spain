from __future__ import annotations

from enum import Enum


class URLs(str, Enum):
    flipcoliving = "https://flipcoliving.com/"
    somosalthena = "https://somosalthena.com/"
    yugo = "https://yugo.com/en-us"
    vita = "https://www.vitastudent.com/en"
    nodis = "https://nodis.es/"


class Pages(str, Enum):
    flipcoliving = "flipcoliving"
    somosalthena = "somosalthena"
    yugo = "yugo"
    vita = "vita"
    nodis = "nodis"


class ScrapingBeeParams(str, Enum):
    RENDER_JS = "render_js"
    EXTRACT_RULES = "extract_rules"


class TenantGenderEnum(Enum):
    INDIFFERENT = "indifferent"
    MALE = "male"
    FEMALE = "female"
    OTHER = "other"


class CancellationPolicyEnum(Enum):
    FLEXIBLE = "flexible"
    STANDARD = "standard"
    STRICT = "strict"


class RentalTypeEnum(Enum):
    COMPLETE = "complete"
    INDIVIDUAL = "individual"


class BedTypeEnum(Enum):
    INDIVIDUAL = "individual"
    DOUBLE = "double"
    QUEEN = "queen"
    KING = "king"


class PaymentCycleEnum(Enum):
    DAILY = "daily"
    FORTNIGHTLY = "fortnightly"
    MONTHLY = "monthly"


class CurrencyCode(Enum):
    USD = "USD"
    CAD = "CAD"
    EUR = "EUR"
    ZWL = "ZWL"


class Languages(Enum):
    SPANISH = 1
    ENGLISH = 2


class PropertyType(Enum):
    STUDIO_ENTIRE_FLAT = "Studio/Entire flat"
    STUDENT_RESIDENCE = "Student residence"
    SHARED_FLAT = "Shared flat"
    COLIVING = "Coliving"
    HOST_FAMILY = "Host family"


class ContractModels(Enum):
    SHORT_TERM = "Short - term"
    MEDIUM_TERM = "Medium-term"
    LONG_TERM = "Long-term"


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
    "2": ["balcony", "balcón", "terraza"],
    "3": ["bbq space", "zona de barbacoa"],
    "4": ["bed linen", "ropa de cama", "sábanas"],
    "5": ["bicycle parking", "aparcamientos de bicicletas"],
    "6": ["bunk beds", "literas"],
    "7": ["cameras", "videovigilancia"],
    "8": ["car parking", "aparcamientos de coches"],
    "9": ["census", "registro en el censo", "inscripción censal"],
    "10": ["cleaning common areas", "limpieza de áreas comunes"],
    "11": ["common areas", "áreas comunes"],
    "12": ["concierge reception", "recepción 24 horas"],
    "13": ["coworking space", "espacio de coworking"],
    "14": ["cradle", "cuna"],
    "15": ["double bed", "cama doble"],
    "16": ["elevator", "ascensor"],
    "17": ["exterior", "exterior", "ventanas exteriores"],
    "18": ["games court", "cancha de juegos", "instalaciones deportivas"],
    "19": ["spa", "spa"],
    "20": ["garden", "jardín","gardens"],
    "21": ["gym", "gimnasio"],
    "22": ["iron", "plancha", "iron board","tabla de planchar"],
    "23": ["living room", "sala de estar"],
    "24": ["lockable rooms", "habitaciones con cerradura"],
    "25": ["mailbox access", "acceso a buzón"],
    "26": ["pillow", "almohada"],
    "27": ["private bath", "baño privado"],
    "28": ["recreational room", "sala de recreación", "zona de juegos"],
    "29": ["room cleaning", "limpieza de habitación"],
    "30": ["shared baths", "baños compartidos"],
    "31": ["single bed", "cama individual"],
    "32": ["smoking alarm", "alarma de humo"],
    "33": ["sofa bed", "sofá cama"],
    "34": ["streaming services", "servicios de streaming"],
    "35": ["study area", "zona de estudio","Private study room"],
    "36": ["swimming pool", "piscina"],
    "37": ["table and chair", "mesa y silla"],
    "38": ["towels", "toallas"],
    "39": ["tv", "televisión", "CCTV"],
    "40": ["two single bed", "dos camas individuales"],
    "41": ["accessible housing", "adapted housing", "housing for disabled"],
    "42": ["wardrobe", "armario", "ropero"],
    "43": ["accessible room", "adapted room", "room for disabled"],
    "44": ["heating system", "sistema de calefaccion", "calefacción", "heating"],
}