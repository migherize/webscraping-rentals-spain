from enum import Enum
from typing import List, Dict
from app.scrapy.common import extract_id_name, search_feature_with_map
from app.config.settings import GlobalConfig
from app.scrapy.common import (
    get_id_from_name,
    get_all_imagenes,
    decode_clean_string,
    extract_area,
    search_location
)
from app.models.enums import PaymentCycleEnum, CurrencyCode
from app.models.schemas import (
    PriceItem,
    Property,
    RentalUnits,
    RentalUnitsCalendarItem,
    LocationAddress,
    ApiKeyItem,
    Text
)

class PropertyTypeColiving(Enum):
    PROPERTY_TYPE = (
        "Pisos",
        "Casas",
        "Edificios",
    )
    OPERATION = "alquiler"


class EquivalencesYugo(Enum):
    FEATURES = {
        "Gym": "Sports facilities",
        "Games Room": "Game room",
        "Common Area": "Common areas",
        "Study Room": "Study area (Chair & table)",
        "Full Board": "Full managed",
        "Wi-Fi": "Wi-fi",
        "Weekly Cleaning": "Cleaning common areas",
        "24-Hour Security": "Video surveillance",
        "On-Site Maintenance": "Maintenance",
        "Laundry": "",  # TODO
        "Postal Service": "Mailbox access",
        "Bike Racks": "Bicycle parking",
        "Common room": "Common areas",
        "Study room": "Shared study area",
        "TV lounge": "Common areas",
        "Dining room": "",  # TODO
        "Coffee bar": "",  # TODO
        "Courtyard": "Terrace / balcony",
        "Beauty spot": "",  # TODO
        "Electricity included": "Electricity",
        "Gas included": "",  # TODO
        "Water included": "Water",
        "Contents Insurance": "",  # TODO
        "Laundry services": "",  # TODO
        "Cleaning services": "Cleaning common areas",
        "High speed internet": "Internet",
        "24-hour hotline": "24hr Concierge Reception",
        "24-hour reception": "24hr Concierge Reception",
        "24-hour security": "Video surveillance",
        "Air conditioning": "Air conditioning",
        "Heating": "Heating system",
        "Accessible entrance": "Wheelchair access",
        "Accessible rooms": "Wheelchair access",
        "Elevator": "Lift",
        "Post collection": "Mailbox access",
        "CCTV": "Video surveillance",
        "Keycard access": "Lockable door",
        "Gated community": "",  # TODO
        "Amazon parcel hub": "Mailbox access",
        "Half-board catering": "Full managed",
        "Study rooms": "Shared study area",
        "Cinema room": "",  # TODO
        "Communal kitchen": "",  # TODO
        "Conference room": "",  # TODO
        "Podcast studio": "",  # TODO
        "Swimming pool": "Swimming pool",
        "Underground station": "",  # TODO
        "Bike storage": "Bicycle parking",
        "Access ramp": "Wheelchair access",
        "Parking (fees apply)": "Car parking",
        "Full-board catering": "Full managed",
    }


def map_property_descriptions(languages, property_descriptions) -> List[Dict]:
    language_dict = {lang.code: lang for lang in languages}
    
    texts = {
        "title_en": None,
        "title_es": None,
        "description_en": None,
        "description_es": None,
    }
    
    for prop in property_descriptions:
        try:
            lang_code = prop.get("language").split("-")[0].upper()
            if prop.get("language") in ["en-us", "ca-es"]:
                continue
            
            language = language_dict.get(lang_code)
            if language:
                title = prop.get("property_name")
                description = prop.get("residence_description")
                
                if lang_code == "EN":
                    texts["title_en"] = title
                    texts["description_en"] = description
                elif lang_code == "ES":
                    texts["title_es"] = title
                    texts["description_es"] = description
            else:
                print(
                    f"Advertencia: No se encontró el idioma para el código '{lang_code}' en la propiedad '{prop.get('property_name')}'."
                )
        except Exception as e:
            print(f"Error al procesar la propiedad '{prop.get('property_name')}': {e}")
    
    return {"Texts": Text(**texts).dict()}


def get_name_by_location(data: List[ApiKeyItem], location: str) -> str:
    """
    Busca en la lista por la ubicación (location) y devuelve el valor de 'name'.

    Args:
        data (list): Lista de diccionarios con las claves 'id', 'name' y 'location'.
        location (str): La ubicación a buscar.

    Returns:
        str: El valor de 'name' correspondiente a la ubicación, o None si no se encuentra.
    """
    for item in data:
        if item.location == location:
            return item.name
    return None

def retrive_lodgerin_property(item, elements, list_api_key):
    api_key = get_name_by_location(list_api_key, item["yugo_space_name"])
    PropertyTypeId = get_id_from_name(
        elements["propertiesTypes"].data, "Apartment / Entire flat", "name_en"
    )
    descriptions = map_property_descriptions(
        elements["languages"].data,
        item["second_items_property"],
    )
    element_feature = extract_id_name(elements["features"].data)
    features_id = search_feature_with_map(
        item["all_feature"],
        element_feature,
        EquivalencesYugo.FEATURES.value,
    )
    address = search_location(item['address_contact_and_email'])

    # clean reference_code
    reference_code = decode_clean_string(item["url_yugo_space"])
    images = get_all_imagenes(item["all_images"])

    if item["tour_virtual"]:
        tour_url = item["tour_virtual"][0]
    else:
        tour_url = None
    property_items = Property(
        referenceCode=reference_code,
        cancellationPolicy=GlobalConfig.CANCELLATION_POLICY,
        rentalType=GlobalConfig.RENTAL_TYPE,
        isActive=True,
        isPublished=True,
        Features=features_id,
        tourUrl=tour_url,
        PropertyTypeId=PropertyTypeId,
        Texts=descriptions,
        Images=images,
        Location=LocationAddress(
            lat=str(address.lat),
            lon=str(address.lon),
            country=address.country,
            countryCode=address.countryCode,
            city=address.city,
            street=address.street,
            state=address.state,
            prefixPhone=address.prefixPhone,
            postalCode=address.postalCode,
            number=address.number,
            fullAddress=address.fullAddress,
            address=address.address,
        ),
        provider="yugo",
        providerRef=reference_code,
    )

    return property_items, api_key


def retrive_lodgerin_rental_units(
    items_property: Property, elements_dict: dict, data_scrapy: list
):
    rental_units = []
    calendar_unit_list = []

    for index, data in enumerate(data_scrapy, start=1):
        if not data.get("api_data_rental_unit", []).get("error", []):
            start_date = data.get("api_data_rental_unit", []).get("tenancy-options", [])[0].get("tenancyOption", [])[0].get("startDate", [])
            end_date = data.get("api_data_rental_unit", []).get("tenancy-options", [])[0].get("tenancyOption", [])[0].get("endDate", [])
            date_text = data.get("api_data_rental_unit", []).get("tenancy-options", [])[0].get("tenancyOption", [])[0].get("formattedLabel", [])
            fromYear = data.get("api_data_rental_unit", []).get("tenancy-options", [])[0].get("fromYear", [])
            toYear = data.get("api_data_rental_unit", []).get("tenancy-options", [])[0].get("toYear", [])
            
            # amenities = data.get("api_data_rental_unit", []).get("residence", []).get("amenities", [])
            # amenities_extras = data.get("api_data_rental_unit", []).get("residence", []).get("amenitiesExternalReference", [])
            # name = data.get("api_data_rental_unit", []).get("room", []).get("name", [])
            amount = data.get("api_data_rental_unit", []).get("room", []).get("minPriceForBillingCycle", [])

        else:
            start_date = "None"
            end_date = "None"
            amount = 1
            date_text = "None"
            fromYear = "None"
            toYear = "None"

        description_unit = data.get("response_data_rental_units", []).get("DESCRIPTION_RENTAL_UNIT", [])
        description_text = description_unit[0] if description_unit else ""

        area = extract_area(description_text)
        area_m2 = int(area) if area is not None else None

        # cost_list = data.get("response_data_rental_units", []).get("COST", [])
        # cost_text = cost_list[0] if cost_list else ""
        # amount = int(extract_cost(cost_text)) if cost_text else 0

        picture = data.get("response_data_rental_units", []).get("picture", [])
        images = get_all_imagenes(picture) if picture else None

        # Price=dict(PriceItem(
        #     contractType=PaymentCycleEnum.MONTHLY.value,
        #     currency=CurrencyCode.EUR.value,
        #     amount=amount,
        #     depositAmount=amount,
        #     reservationAmount=GlobalConfig.INT_ZERO,
        #     minPeriod=GlobalConfig.INT_ONE,
        #     paymentCycle=PaymentCycleEnum.MONTHLY.value
        # ))
        # print("Price",Price)
        # print("Price",PaymentCycleEnum.MONTHLY.value)

        data_rental_unit = RentalUnits(
            PropertyId=items_property.id,
            referenceCode=f"{items_property.referenceCode}-{index:03}",
            areaM2=area_m2,
            isActive=True,
            isPublished=True,
            Price=PriceItem(
                contractType=PaymentCycleEnum.MONTHLY.value,
                currency=CurrencyCode.EUR.value,
                amount=amount,
                depositAmount=amount,
                reservationAmount=GlobalConfig.INT_ZERO,
                minPeriod=GlobalConfig.INT_ONE,
                paymentCycle=PaymentCycleEnum.MONTHLY.value
            ),
            # Price={
            #     "contractType": "monthly",
            #     "currency": "EUR",
            #     "amount": 150,
            #     "depositAmount": 150,
            #     "reservationAmount": 150,
            #     "discountPercent": 0,
            #     "minPeriod": 30,
            #     "maxPeriod": 90,
            #     "paymentCycle": "monthly",
            # },
            # ContractsModels=[
            #     ContractModel(
            #         PropertyBusinessModelId=funcs.get_elements_types(
            #             settings.MODELS_CONTRACT, elements_dict["contract_types"]
            #         ),
            #         currency=CurrencyCode.EUR.value,
            #         amount=amount,
            #         depositAmount=amount,
            #         reservationAmount=settings.INT_ZERO,
            #         minPeriod=settings.INT_ONE,
            #         paymentCycle=PaymentCycleEnum.MONTHLY.value,
            #         extras=[],
            #     )
            # ],
            Features=items_property.Features,
            Texts=items_property.Texts,
            Images=images
        )
        rental_units.append(data_rental_unit)
        date_items = RentalUnitsCalendarItem(
            summary=f"Blocked until {fromYear} - {toYear}",
            description=date_text,
            startDate=start_date,
            endDate=end_date,
        )
        calendar_unit_list.append(date_items)

    return rental_units, calendar_unit_list
