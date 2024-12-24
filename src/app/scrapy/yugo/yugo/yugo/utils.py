from urllib.parse import urlparse
from enum import Enum
from deepparse import Deepparse

import app.utils.funcs as funcs
from app.scrapy.common import parse_elements, extract_id_name, search_feature_with_map
import app.utils.constants as constants
from app.scrapy.common import read_json, get_id_from_name, get_all_imagenes
from app.models.schemas import (
    ContractModel,
    Property,
    RentalUnits,
    DatePayloadItem,
    mapping,
)

# from .utils import (
#     get_data_json,
#     get_month,
#     retrive_lodgerin_property,
#     retrive_lodgerin_rental_units,
# )


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


def map_property_descriptions(languages, property_descriptions):
    print("languages", languages)
    language_dict = {lang["code"]: lang for lang in languages}
    print("language_dict", language_dict)

    result = []

    for prop in property_descriptions:
        try:
            lang_code = prop.get("language").split("-")[0].upper()
            if prop.get("language") == "en-us" or prop.get("language") == "ca-es":
                continue
            language = language_dict.get(lang_code)
            if language:
                language_id = language["id"]
                title = prop.get("property_name")
                description = prop.get("residence_description")
                result.append(
                    {
                        "LanguagesId": language_id,
                        "title": title,
                        "description": description,
                    }
                )
            else:
                print(
                    f"Advertencia: No se encontró el idioma para el código '{lang_code}' en la propiedad '{prop.get('property_name')}'."
                )
        except Exception as e:
            print(f"Error al procesar la propiedad '{prop.get('property_name')}': {e}")

    return result


def retrive_lodgerin_property(item, elements):
    item = item["items_output"]
    PropertyTypeId = get_id_from_name(
        elements["property_types"], "Studio/Entire flat", "name"
    )
    descriptions = map_property_descriptions(
        elements["languages"]["data"],
        item["second_items_property"],
    )

    element_feature = extract_id_name(elements["features"]["data"])
    features_id = search_feature_with_map(
        item["all_feature"],
        element_feature,
        EquivalencesYugo.FEATURES.value,
    )

    parsed_url = urlparse(item["url_yugo_space"])
    path = parsed_url.path
    referenceCode = path.replace("/en-us/global/spain/", "").replace("/", "-")
    images = get_all_imagenes(item['all_images'])
    if item['tour_virtual']:
        tour_url = item['tour_virtual'][0]
    else:
        tour_url = ""
    property_items = Property(
        referenceCode=referenceCode,
        cancellationPolicy=constants.CANCELLATION_POLICY,
        rentalType=constants.RENTAL_TYPE,
        isActive=True,
        isPublished=True,
        Features=features_id,
        tourUrl=tour_url,
        PropertyTypeId=PropertyTypeId,
        Descriptions=descriptions,
        Images=images,
        # Location=parse_address(item['address_contact_and_email']),#TODO
        provider="yugo",
        providerRef=referenceCode,
    )

    return property_items


if __name__ == "__main__":
    import json
    with open(
        "/Users/mherize/squadmakers/logderin/WebScrapingforRentalPlatforms/local/data/yugo/items.json",
        "r",
        encoding="utf-8",
    ) as archivo:
        items = json.load(archivo)

    elements_dict = parse_elements(read_json()[0], mapping)
    api_key = elements_dict["api_key"]["data"][0]["name"]

    for data in items:
        # Property
        data_property = retrive_lodgerin_property(data, elements_dict)
        property_id = funcs.save_property(data_property, api_key)
        data_property.id = property_id
        
        # RentalUnit
        # data_rental_units = retrive_lodgerin_rental_units(
        #     data_property, elements_dict, cost
        # )
        # rental_unit_id = funcs.save_rental_unit(data_rental_units, api_key)
        # data_rental_units.id = rental_unit_id
        
        # Schedule
        # start_date, end_date, month = get_month()
        # calendar_unit = DatePayloadItem(
        #     summary=f"Blocked until {start_date}",
        #     description=f"Available from {month}",
        #     startDate=start_date,
        #     endDate=end_date,
        # )
        # funcs.check_and_insert_rental_unit_calendar(
        #     rental_unit_id, calendar_unit, api_key
        # )
