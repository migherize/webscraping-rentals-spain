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


class ConfigErrorScraper(Enum):
    """
    Señales que puede detectar errores en los logs de las arañas
    """
    REGEX_ERROR = r"] ERROR:|Request error occurred"
# TODO: elimnar luego de probar flipcoling y vita
# feature_map = {
#     "1": ["airConditioning", "air conditioning", "aire acondicionado"],
#     "2": ["balcony", "balcón", "terraza"],
#     "3": ["bbq space", "zona de barbacoa"],
#     "4": ["bed linen", "ropa de cama", "sábanas"],
#     "5": ["bicycle parking", "aparcamientos de bicicletas"],
#     "6": ["bunk beds", "literas"],
#     "7": ["cameras", "videovigilancia"],
#     "8": ["car parking", "aparcamientos de coches"],
#     "9": ["census", "registro en el censo", "inscripción censal"],
#     "10": ["cleaning common areas", "limpieza de áreas comunes"],
#     "11": ["commonAreas", "common areas", "áreas comunes"],
#     "12": ["concierge reception", "recepción 24 horas"],
#     "13": ["coworking space", "espacio de coworking"],
#     "14": ["cradle", "cuna"],
#     "15": ["double bed", "cama doble"],
#     "16": ["elevator", "ascensor"],
#     "17": ["exterior", "ventanas exteriores"],
#     "18": ["games court", "cancha de juegos", "instalaciones deportivas"],
#     "19": ["spa", "spa"],
#     "20": ["garden", "jardín", "gardens"],
#     "21": ["gym", "gimnasio"],
#     "22": ["iron", "plancha", "iron board", "tabla de planchar"],
#     # "23": ["", ""],
#     "24": ["livingRoom", "living room", "sala de estar"],
#     "25": ["lockable rooms", "habitaciones con cerradura"],
#     "26": ["mailboxAccess", "mailbox access", "acceso a buzón"],
#     "27": ["pillow", "almohada"],
#     "28": ["private bath", "baño privado"],
#     "29": ["recreational room", "sala de recreación", "zona de juegos"],
#     "30": ["room cleaning", "limpieza de habitación"],
#     "31": ["sharedBaths", "shared baths", "baños compartidos"],
#     "32": ["single bed", "cama individual"],
#     "33": ["smoking alarm", "alarma de humo"],
#     "34": ["sofaBed", "sofa bed", "sofá cama"],
#     "35": ["streaming services", "servicios de streaming"],
#     "36": ["studyArea", "study area", "zona de estudio", "Private study room"],
#     "37": ["swimmingPool", "swimming pool", "piscina"],
#     "38": ["table and chair", "mesa y silla"],
#     "39": ["towels", "toallas"],
#     "40": ["tv", "televisión", "CCTV"],
#     "41": ["two single bed", "dos camas individuales"],
#     "42": [
#         "accessibleHousing",
#         "accessible housing",
#         "adapted housing",
#         "housing for disabled",
#     ],
#     "43": ["wardrobe", "armario", "ropero"],
#     "44": ["accessible room", "adapted room", "room for disabled"],
#     "45": [
#         "heatingSystem",
#         "heating system",
#         "sistema de calefaccion",
#         "calefacción",
#         "heating",
#     ],
# }

feature_map_rental_units = {
    "1": "airConditioning",
    "4": "bedLinen",
    "6": "bunkBeds",
    "14": "cradle",
    "15": "doubleBed",
    "17": "exterior",
    "25": "lockableRooms",
    "27": "pillow",
    "28": "privateBath",
    "30": "roomCleaning",
    "32": "singleBed",
    "33": "smokingAlarm",
    "36": "studyArea",
    "38": "tableAndChair",
    "39": "towels",
    "40": "tv",
    "41": "twoSingleBed",
    "43": "wardrobe",
    "44": "accessibleRoom",
    "45": "heatingSystem",
}

feature_map = {
    "1": "airConditioning",
    "2": "balcony",
    "3": "bbq space",
    "4": "bed linen",
    "5": "bicycle parking",
    "6": "bunk beds",
    "7": "cameras",
    "8": "car parking",
    "9": "census",
    "10": "cleaning common areas",
    "11": "commonAreas",
    "12": "concierge reception",
    "13": "coworking space",
    "14": "cradle",
    "15": "double bed",
    "16": "elevator",
    "17": "exterior",
    "18": "games court",
    "19": "spa",
    "20": "garden",
    "21": "gym",
    "22": "iron",
    "24": "livingRoom",
    "25": "lockable rooms",
    "26": "mailboxAccess",
    "27": "pillow",
    "28": "private bath",
    "29": "recreational room",
    "30": "room cleaning",
    "31": "sharedBaths",
    "32": "single bed",
    "33": "smoking alarm",
    "34": "sofaBed",
    "35": "streaming services",
    "36": "studyArea",
    "37": "swimmingPool",
    "38": "table and chair",
    "39": "towels",
    "40": "tv",
    "41": "two single bed",
    "42": "accessibleHousing",
    "43": "wardrobe",
    "44": "accessible room",
    "45": "heatingSystem",
}

custom_map = {
    "property.provider_ref": "id",
    "property.lodgerin_ref": "referenceCode",
    "property.address": "Location.address",
    "property.address_number": "Location.number",
    "property.floor": None,
    "property.door_number": None,
    "property.postal_code": "Location.postalCode",
    "property.city": "Location.city",
    "Accommodation type": None,
    "property.PropertyTypeId": "PropertyTypeId",
    "property.estates_number": None,
    "property.numBathrooms": "numBathrooms",
    "property.elevator": "Features.elevator",
    "property.balcony": "Features.balcony",
    "property.exterior": "Features.exterior",
    "property.swimmingPool": "Features.swimmingPool",
    "property.airConditioning": "Features.airConditioning",
    "property.heatingSystem": "Features.heatingSystem",
    "property.cameras": "Features.cameras",
    "property.livingRoom": "Features.livingRoom",
    "property.sharedBaths": "Features.sharedBaths",
    "property.commonAreas": "Features.commonAreas",
    "property.sofaBed": "Features.sofaBed",
    "property.studyArea": "Features.studyArea",
    "property.towels": "Features.towels",
    "property.accessibleHousing": "Features.accessibleHousing",
    "property.tv": "Features.tv",
    "property.mailboxAccess": "Features.mailboxAccess",
    "property.maxOccupancy": "maxOccupancy",
    "property.minAge": None,
    "property.areaM2": "areaM2",
    "property.areaM2Available": "areaM2Available",
    "property.pets": None,
    "property.electricity": None,
    "property.couples": None,
    "property.instantBooking": None,
    "property.smoke": None,
    "property.water": None,
    "property.wifi": None,
    "property.gas": None,
    "property.guestNight": None,
    "property.partyAllowed": None,
    "property.kitchen": None,
    "property.dishwasher": None,
    "property.dryer": None,
    "property.microwave": None,
    "property.oven": None,
    "property.stove": None,
    "property.washer": None,
    "ru.contractType": "contractType",
    "property.Languages": None,
    "property.occupationTenant": None,
    "property.rentalType": None,
    "property.tenantGender": None,
    "property.minPeriod": None,
    "property.cancellationPolicy": None,
    "property.check-in": None,
    "property.videoUrl": "videoUrl",
    "property.tourUrl": "toururl",
    "property.images_folder": None,
    "property.images": "Images",
    "ru.currency": "Price.currency",
    "ru.provider_ref": "id",
    "ru.lodgerin_ref": "referenceCode",
    "ru.rooms": None,
    "ru.areaM2": "areaM2",
    "ru.areaM2Available": "areaM2Available",
    "ru.typeSize": "typeSize",
    "ru.maxCapacity": "maxCapacity",
    "ru.roomType": None,
    "ru.bedType": None,
    "ru.amount": "Price.amount",
    "ru.reservationAmount": "Price.reservationAmount",
    "ru.landlordFee": None,
    "ru.discountPercent": "Price.discountPercent",
    "ru.paymentCycle": "Price.paymentCycle",
    "ru.extra_costs": None,
    "ru.depositAmount": "Price.depositAmount",
    "ru.privateBath": None,
    "ru.bedLinen": None,
    "ru.studyArea": None,
    "ru.tableAndChair": None,
    "ru.terrace": None,
    "ru.wardrobe": None,
    "ru.exterior": None,
    "ru.lockableRooms": None,
    "ru.airConditioning": None,
    "ru.tv": None,
    "ru.heatingSystem": None,
    "ru.roomCleaning": None,
    "ru.balcony": None,
    "ru.cradle": None,
    "ru.pillow": None,
    "ru.smokingAlarm": None,
    "ru.twoSingleBed": None,
    "ru.accessibleRoom": None,
    "ru.towels": None,
    "ru.cleaningFee": None,
    "ru.waterFee": None,
    "ru.electricityFee": None,
    "ru.gasFee": None,
    "ru.internetFee": None,
    "ru.urlICalSync": "urlICalSync",
    "ru.images_folder": None,
    "ru.images": "Images",
}

friendly_headers = [
    "Referencia Proveedor vivienda",
    "Referencia Arrento  vivienda",
    "Address",
    "Address number",
    "Floor",
    "Door number/letter",
    "Postal code",
    "City",
    "Accommodation type",
    "Unnamed: 10_level_1",
    "House bedrooms (Number)",
    "House baths (Number)",
    "Lift / Elavator",
    "Terrace / balcony",
    "Exterior",
    "Swimming Pool",
    "Air conditioning",
    "Heating system",
    "Cameras",
    "LivingRoom",
    "Shared Baths",
    "Common areas",
    "Sofa Bed",
    "Study Area",
    "Towels",
    "Accessible Housing",
    "Television",
    "Mailbox access",
    "Maximum occupancy",
    "Tenants minimun age",
    "Area M2",
    "Area M2 Available",
    "Pets allowed",
    "Electricity",
    "Couples",
    "Instant Booking",
    "Smoking allowed",
    "Water",
    "Wifi",
    "Gas",
    "Guests night allowed",
    "Party Allowed",
    "Kitchen",
    "Dishwasher",
    "Dryer",
    "Microwave",
    "Oven",
    "Stove",
    "Washer",
    "Calculation of the monthly rent",
    "Languages spoken by owner",
    "Occupation Tenant",
    "Rental Type",
    "Tenant Gender",
    "Minimun stay (Days amount)",
    "CANCELLATION POLICY",
    "Check-in",
    "Video tour URL",
    "Tour 360 URL (matterport)",
    "Common areas images folder",
    "",
    "Currency",
    "Referencia Proveedor habitación ",
    "Referencia Lodgerin habitación ",
    "Amount of room the same type (only residences)",
    "Area M2",
    "Area M2 Available",
    "Type Size",
    "Max Capacity",
    "Room type",
    "Bed type",
    "Month price (€)",
    "Booking price (€) (Optional) / Reservation Amount",
    "Landlord Fee",
    "Discount Percent(Optional)",
    "Payment Cycle",
    "Extra costs (€) (Optional)",
    "Deposit (€)",
    "Private bath",
    "Bedlinen",
    "Study area",
    "(Chair & table)",
    "Private balcony/terrace",
    "Wardrobe",
    "Exterior (Room)",
    "Lockable door",
    "Air conditioning (Room)",
    "Television (Room)",
    "Heating (Included)",
    "Room Cleaning(Included)",
    "Balcony / terrace (Included)",
    "Cradle",
    "Pillow",
    "Smoking Alarm",
    "Two Single Bed",
    "Accessible Room",
    "Towels",
    "Cleaning Fee",
    "Water Fee",
    "Electricity Fee",
    "Gas Fee",
    "Internet Fee",
    "Disponibilidad (iCal URL)",
    "Room images folder",
]