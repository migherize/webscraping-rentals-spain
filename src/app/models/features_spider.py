from enum import Enum
from math import log


class LodgerinFeatures(Enum):
    FEATURE_AIR_CONDITIONING = "airConditioning"
    FEATURE_BALCONY = "balcony"
    FEATURE_BBQ_SPACE = "bbqSpace"
    FEATURE_BED_LINEN = "bedLinen"
    FEATURE_BICYCLE_PARKING = "bicycleParking"
    FEATURE_BUNK_BEDS = "bunkBeds"
    FEATURE_CAMERAS = "cameras"
    FEATURE_CAR_PARKING = "carParking"
    FEATURE_CENSUS = "census"
    FEATURE_CLEANING_COMMON_AREAS = "cleaningCommonAreas"
    FEATURE_COMMON_AREAS = "commonAreas"
    FEATURE_CONCIERGE_RECEPTION = "conciergeReception"
    FEATURE_COWORKING_SPACE = "coworkingSpace"
    FEATURE_CRADLE = "cradle"
    FEATURE_DOUBLE_BED = "doubleBed"
    FEATURE_ELEVATOR = "elevator"
    FEATURE_EXTERIOR = "exterior"
    FEATURE_GAMES_COURT = "gamesCourt"
    FEATURE_SPA = "spa"
    FEATURE_GARDEN = "garden"
    FEATURE_GYM = "gym"
    FEATURE_IRON = "iron"
    FEATURE_LIVING_ROOM = "livingRoom"
    FEATURE_LOCKABLE_ROOMS = "lockableRooms"
    FEATURE_MAILBOX_ACCESS = "mailboxAccess"
    FEATURE_PILLOW = "pillow"
    FEATURE_PRIVATE_BATH = "privateBath"
    FEATURE_RECREATIONAL_ROOM = "recreationalRoom"
    FEATURE_ROOM_CLEANING = "roomCleaning"
    FEATURE_SHARED_BATHS = "sharedBaths"
    FEATURE_SINGLE_BED = "singleBed"
    FEATURE_SMOKING_ALARM = "smokingAlarm"
    FEATURE_SOFA_BED = "sofaBed"
    FEATURE_STREAMING_SERVICES = "streamingServices"
    FEATURE_STUDY_AREA = "studyArea"
    FEATURE_SWIMMING_POOL = "swimmingPool"
    FEATURE_TABLE_AND_CHAIR = "tableAndChair"
    FEATURE_TOWELS = "towels"
    FEATURE_TV = "tv"
    FEATURE_TWO_SINGLE_BED = "twoSingleBed"
    FEATURE_ACCESSIBLE_HOUSING = "accessibleHousing"
    FEATURE_WARDROBE = "wardrobe"
    FEATURE_ACCESSIBLE_ROOM = "accessibleRoom"
    FEATURE_HEATING_SYSTEM = "heatingSystem"


class EquivalencesNodis:
    FEATURES = {
        "Piscina": LodgerinFeatures.FEATURE_SWIMMING_POOL.value,
        "Rooftop": LodgerinFeatures.FEATURE_BALCONY.value,
        "Gimnasio": LodgerinFeatures.FEATURE_GYM.value,
        "Jardin exterior": LodgerinFeatures.FEATURE_GARDEN.value,
        "Jardín exterior": LodgerinFeatures.FEATURE_GARDEN.value,
        "chill out": LodgerinFeatures.FEATURE_RECREATIONAL_ROOM.value,
        "Sala": LodgerinFeatures.FEATURE_LIVING_ROOM.value,
        "audiovisuales": LodgerinFeatures.FEATURE_TV.value,
        "Salones privados": LodgerinFeatures.FEATURE_LIVING_ROOM.value,
        "Biblioteca": LodgerinFeatures.FEATURE_STUDY_AREA.value,
        "Salas de trabajo y coworking": LodgerinFeatures.FEATURE_COWORKING_SPACE.value,
        "Zona de juegos": LodgerinFeatures.FEATURE_GAMES_COURT.value,
        "Parking": LodgerinFeatures.FEATURE_CAR_PARKING.value,
        "Área co-working": LodgerinFeatures.FEATURE_COWORKING_SPACE.value,
        "Salas de estudio": LodgerinFeatures.FEATURE_STUDY_AREA.value,
        "Aparcamiento": LodgerinFeatures.FEATURE_CAR_PARKING.value,
        "Área de juegos": LodgerinFeatures.FEATURE_GAMES_COURT.value,
        "Gaming zone": LodgerinFeatures.FEATURE_GAMES_COURT.value,
        "Terraza": LodgerinFeatures.FEATURE_BALCONY.value,
        "Sala de cine": None,
        "self service": None,
        "Comedor": None,
        "Food Lab – cocina común": None,
        "Comedor privado": None,
        "Área de vending": None,
        "Trastero": None,
        "Lavanderia": None,
        "Lavandería autoservicio": None,
    }


class FeaturesSomosAlthena:
    FEATURES = {
        "Banos": LodgerinFeatures.FEATURE_PRIVATE_BATH.value,
        "AireAcondicionado": LodgerinFeatures.FEATURE_AIR_CONDITIONING.value,
        "Exterior": LodgerinFeatures.FEATURE_EXTERIOR.value,
        "PiscinaPrivada": LodgerinFeatures.FEATURE_SWIMMING_POOL.value,
        "Calefaccion": LodgerinFeatures.FEATURE_HEATING_SYSTEM.value,
        "Ascensor": LodgerinFeatures.FEATURE_ELEVATOR.value,
        "Conserje": LodgerinFeatures.FEATURE_CONCIERGE_RECEPTION.value,
        "Alarma": LodgerinFeatures.FEATURE_SMOKING_ALARM.value,
        "Vigilancia24h": LodgerinFeatures.FEATURE_CAMERAS.value,
        "AccesoDiscapacitados": LodgerinFeatures.FEATURE_ACCESSIBLE_HOUSING.value,
        "Terrazas": LodgerinFeatures.FEATURE_BALCONY.value,
        "ZonasComunes": LodgerinFeatures.FEATURE_COMMON_AREAS.value,
        "AdmiteMascotas": None,
        "Cocina": None,
        "Internet": None,
        "ZonaInfantil": None,
        "Gas": None,
        "Agua": None,
        "Luz": None,
        "Amueblado": None,
    }


class EquivalencesYugo:
    FEATURES = {
        "Gym": LodgerinFeatures.FEATURE_GYM.value,
        "Games Room": LodgerinFeatures.FEATURE_GAMES_COURT.value,
        "BBQ area": LodgerinFeatures.FEATURE_BBQ_SPACE.value,
        "Fire pit": LodgerinFeatures.FEATURE_BBQ_SPACE.value,
        "Common Area": LodgerinFeatures.FEATURE_COMMON_AREAS.value,
        "Study Room": LodgerinFeatures.FEATURE_STUDY_AREA.value,
        "Weekly Cleaning": LodgerinFeatures.FEATURE_CLEANING_COMMON_AREAS.value,
        "24-Hour Security": LodgerinFeatures.FEATURE_CAMERAS.value,
        "Postal Service": LodgerinFeatures.FEATURE_MAILBOX_ACCESS.value,
        "Bike Racks": LodgerinFeatures.FEATURE_BICYCLE_PARKING.value,
        "Common room": LodgerinFeatures.FEATURE_COMMON_AREAS.value,
        "TV lounge": LodgerinFeatures.FEATURE_COMMON_AREAS.value,
        "Courtyard": LodgerinFeatures.FEATURE_BALCONY.value,
        "Cleaning services": LodgerinFeatures.FEATURE_CLEANING_COMMON_AREAS.value,
        "24-hour hotline": LodgerinFeatures.FEATURE_CONCIERGE_RECEPTION.value,
        "24-hour reception": LodgerinFeatures.FEATURE_CONCIERGE_RECEPTION.value,
        "24-hour security": LodgerinFeatures.FEATURE_CAMERAS.value,
        "Air conditioning": LodgerinFeatures.FEATURE_AIR_CONDITIONING.value,
        "Heating": LodgerinFeatures.FEATURE_HEATING_SYSTEM.value,
        "Accessible entrance": LodgerinFeatures.FEATURE_ACCESSIBLE_HOUSING.value,
        "Accessible rooms": LodgerinFeatures.FEATURE_ACCESSIBLE_HOUSING.value,
        "Elevator": LodgerinFeatures.FEATURE_ELEVATOR.value,
        "Post collection": LodgerinFeatures.FEATURE_MAILBOX_ACCESS.value,
        "CCTV": LodgerinFeatures.FEATURE_CAMERAS.value,
        "Amazon parcel hub": LodgerinFeatures.FEATURE_MAILBOX_ACCESS.value,
        "Swimming pool": LodgerinFeatures.FEATURE_SWIMMING_POOL.value,
        "Bike storage": LodgerinFeatures.FEATURE_BICYCLE_PARKING.value,
        "Access ramp": LodgerinFeatures.FEATURE_ACCESSIBLE_HOUSING.value,
        "Parking (fees apply)": LodgerinFeatures.FEATURE_CAR_PARKING.value,
        "Gaming stations": LodgerinFeatures.FEATURE_GAMES_COURT.value,
        "Outside terrace": LodgerinFeatures.FEATURE_BALCONY.value,
        "Rooftop terrace": LodgerinFeatures.FEATURE_BALCONY.value,
        "Parking (free)": LodgerinFeatures.FEATURE_CAR_PARKING.value,
        "Movie room": LodgerinFeatures.FEATURE_RECREATIONAL_ROOM.value,
        "Garden": LodgerinFeatures.FEATURE_GARDEN.value,
        "Hot tub": None,
        "Pool": None,
        "Pet-friendly": None,
        "Dog park": None,
        "Washing machine": None,
        "Dryer": None,
        "Park": None,
        "Skyline view": None,
        "Metro station": None,
        "High speed Wifi": None,
        "Yoga studio": None,
        "Karaoke room": None,
        "Bus": None,
        "Shuttle Bus": None,
        "Tram": None,
        "All utilities included": None,
        "Shower": None,
        "Desk": None,
        "Ensuite": None,
        "eycard entry": None,
        "Mattress": None,
        "Mirror": None,
        "Private bathroom": None,
        "Smoke detector": None,
        "Wardrobe": None,
        "Fridge freezer": None,
        "Microwave": None,
        "Hob/Oven": None,
        "Fitness studio": None,
        "Sauna": None,
        "Oven/Grill": None,
        "Volleyball court": None,
        "Basketball court": None,
        "Tennis court": None,
        "Train station": None,
        "Walk to campus": None,
        "Cycle to campus": None,
        "Drive to campus": None,
        "Electricity included": None,
        "High speed internet": None,
        "Keycard access": None,
        "On-Site Maintenance": None,
        "Study room": None,
        "Study rooms": None,
        "Half-board catering": None,
        "Full Board": None,
        "Wi-Fi": None,
        "Full-board catering": None,
        "Gated community": None,
        "Cinema room": None,
        "Communal kitchen": None,
        "Conference room": None,
        "Podcast studio": None,
        "Underground station": None,
        "Laundry": None,
        "Dining room": None,
        "Coffee bar": None,
        "Beauty spot": None,
        "Gas included": None,
        "Water included": None,
        "Contents Insurance": None,
        "Laundry services": None,
    }


class EquivalencesFlipColinving:
    FEATURES = {
        "amazing shared spaces": LodgerinFeatures.FEATURE_RECREATIONAL_ROOM.value,
        "bbq / grill": LodgerinFeatures.FEATURE_BBQ_SPACE.value,
        "bathroom": LodgerinFeatures.FEATURE_PRIVATE_BATH.value,
        "bicycle parking": LodgerinFeatures.FEATURE_BICYCLE_PARKING.value,
        "blazing fast wi-fi": LodgerinFeatures.FEATURE_STREAMING_SERVICES.value,
        "close to bus station": LodgerinFeatures.FEATURE_ACCESSIBLE_HOUSING.value,
        "coffee machine": LodgerinFeatures.FEATURE_TABLE_AND_CHAIR.value,
        "cleaning and maintenance": LodgerinFeatures.FEATURE_ROOM_CLEANING.value,
        "dryer": LodgerinFeatures.FEATURE_SOFA_BED.value,
        "exclusive benefits": None,
        "fitness center": LodgerinFeatures.FEATURE_GYM.value,
        "flexible leases": LodgerinFeatures.FEATURE_CONCIERGE_RECEPTION.value,
        "fridge": LodgerinFeatures.FEATURE_TV.value,
        "hangers": None,
        "hot and cold a/c": LodgerinFeatures.FEATURE_AIR_CONDITIONING.value,
        "iron": LodgerinFeatures.FEATURE_IRON.value,
        "keyless access": LodgerinFeatures.FEATURE_LOCKABLE_ROOMS.value,
        "linens": LodgerinFeatures.FEATURE_BED_LINEN.value,
        "microwave": LodgerinFeatures.FEATURE_STREAMING_SERVICES.value,
        "non smoking": LodgerinFeatures.FEATURE_SMOKING_ALARM.value,
        "no pets allowed": LodgerinFeatures.FEATURE_CENSUS.value,
        "on-site laundry": LodgerinFeatures.FEATURE_CLEANING_COMMON_AREAS.value,
        "oven": LodgerinFeatures.FEATURE_STUDY_AREA.value,
        "private bedroom": LodgerinFeatures.FEATURE_PRIVATE_BATH.value,
        "private desk": LodgerinFeatures.FEATURE_STUDY_AREA.value,
        "quick repairs service": LodgerinFeatures.FEATURE_CLEANING_COMMON_AREAS.value,
        "shared areas daily cleaning": LodgerinFeatures.FEATURE_CLEANING_COMMON_AREAS.value,
        "smart tv": LodgerinFeatures.FEATURE_TV.value,
        "stove": LodgerinFeatures.FEATURE_SOFA_BED.value,
        "towels": LodgerinFeatures.FEATURE_TOWELS.value,
        "washer": None,
        "access exclusive events": None,
        "fully equipped kitchen": None,
        "fully furnished": None,
        "Close to metro station": None,
        "Coworking": None,
        "Shared areas weekly cleaning": None,
        "Hot tub": None,
        "Dishwasher":None,
        "Guesthouse":None,
        "Couples are allowed":None,
        "Private lockers":None,
        "Silence":None,
        "Essential services":None,
        "Cable TV":None,
        "Professionals network":None,
    }


class EquivalencesVitaStudents:
    FEATURES = {
        "Spacious hub": LodgerinFeatures.FEATURE_RECREATIONAL_ROOM.value,
        "Private study room": LodgerinFeatures.FEATURE_STUDY_AREA.value,
        "Coffee lounge": LodgerinFeatures.FEATURE_RECREATIONAL_ROOM.value,
        "Gym": LodgerinFeatures.FEATURE_GYM.value,
        "Courtyard": LodgerinFeatures.FEATURE_GARDEN.value,
        "Gardens": LodgerinFeatures.FEATURE_GARDEN.value,
        "Smart TV": LodgerinFeatures.FEATURE_TV.value,
        "Movie room": LodgerinFeatures.FEATURE_RECREATIONAL_ROOM.value,
        "Dance studio": LodgerinFeatures.FEATURE_RECREATIONAL_ROOM.value,
        "Exclusive rooftop terrace": LodgerinFeatures.FEATURE_BALCONY.value,
        "Outside terrace": LodgerinFeatures.FEATURE_BALCONY.value,
        "Air conditioning": LodgerinFeatures.FEATURE_AIR_CONDITIONING.value,
        "Ensuite bathroom - shower, mirror, sink, toilet": None,
        "VIP discounts": None,
        "Kitchen - microwave oven  hob  sink  fridge freezer": None,
        "Non-opening window": None,
        "Kitchenette – sink  microwave  fridge freezer": None,
        "Pool table": None,
        "Mahjong tables": None,
        "Ensuite bathroom": None,
        "Pinboard": None,
        "Three quarter bed": None,
        "Secure key fob access": None,
        "Ensuite bathroom - shower  mirror  sink  toilet": None,
        "Kitchenette - sink  microwave  fridge freezer": None,
        "Pool & table tennis tables": None,
        "Private dining room": None,
        "Laundry room": None,
        "CCTV": None,
        "Early access to communal spaces when you book": None,
        "Free weekday breakfast": None,
        "Free bi-weekly housekeeping": None,
        "Free events": None,
        "24/7 on-site team": None,
        "Superfast wifi": None,
        "Desk": None,
        "Desk chair": None,
        "Double bed": None,
        "Ensuite bathroom – shower  mirror  sink  toilet": None,
        "Kitchen – microwave oven  hob  sink  fridge freezer": None,
        "Mirror": None,
        "Opening window": None,
        "Underbed storage": None,
        "Wardrobe": None,
        "Bin": None,
        "Bed": None,
        "Bike store": None,
        "24hr parcel room": None,
        "Free tea & coffee": None,
        "Online doctor service": None,
        "High desk": None,
        "High desk chair": None,
    }
