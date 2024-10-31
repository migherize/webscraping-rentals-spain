import os
import re
import json
import ast
import logging
from typing import Union, List
from enum import Enum
from pydantic import BaseModel
import app.utils.constants as constants
from app.models.enums import feature_map, CurrencyCode, PaymentCycleEnum
from app.models.schemas import (
    Property,
    RentalUnits,
    ContractModel,
    Description,
    Image,
    LocationAddress,
    DatePayload,
    DatePayloadItem
)
from app.utils.funcs import find_feature_keys, get_elements_types


class RegexPatterns(str, Enum):
    RATE = r"[\d,.]+€"
    BEDROOMS = r"habitaciones|bedrooms"
    AREA_SQM = r"[Mm]2|[Ss][Qq][Mm]"
    NON_DIGITS = r"[^\d.,]+"


class RoomData(BaseModel):
    areaM2: int
    amount: str
    schedule: str
    title: str
    images: List[str]


def remove_duplicate_urls(url_list: list) -> list:
    cleaned_urls = []
    seen = set()

    for url in url_list:
        clean_url = re.sub(r"-\d+x\d+\.jpg", ".jpg", url.split()[0])
        clean_url = re.sub(r"-\d+x\d+\.png", ".png", url.split()[0])

        if clean_url not in seen:  # If the item has not been seen
            seen.add(clean_url)  # Add it to the set
            cleaned_urls.append(clean_url)  # Add it to the result list

    return cleaned_urls


def byte_string_to_dict(byte_string: bytes) -> dict:
    """
    Converts a byte string containing a Python-like dictionary to a valid JSON object.

    Args:
        byte_string (bytes): A byte string that represents a dictionary in Python format.

    Returns:
        dict: A dictionary representation of the byte string.

    Raises:
        ValueError: If the byte string cannot be decoded or evaluated.
    """
    try:
        decoded_string = byte_string.decode("utf-8")
        python_dict = ast.literal_eval(decoded_string)

        if not isinstance(python_dict, dict):
            raise ValueError("Decoded string does not represent a valid dictionary.")

        return python_dict

    except (UnicodeDecodeError, ValueError, SyntaxError) as e:
        print("Failed to convert byte string to dictionary: %s", e)
        raise ValueError(f"Invalid byte string provided: {str(e)}")


def extract_features(all_data: list):
    neighborhood = all_data[0]
    rate_min = ""
    rate_max = ""
    area_sqm = ""
    bedrooms = ""

    for data in all_data:
        if re.findall(RegexPatterns.RATE.value, data):
            rates = re.findall(RegexPatterns.RATE.value, data)
            rate_min, rate_max = rates

        if re.search(RegexPatterns.BEDROOMS.value, data):
            bedrooms = re.sub(RegexPatterns.NON_DIGITS.value, "", data).strip()

        if re.search(RegexPatterns.AREA_SQM.value, data):
            area_sqm = re.sub(RegexPatterns.AREA_SQM.value, "", data).strip()

    rate_max = re.sub(r'[^\d,.]', '', rate_max)
    rate_min = re.sub(r'[^\d,.]', '', rate_min)

    return neighborhood, rate_min, rate_max, area_sqm, bedrooms


def refine_extractor_data(
    data: dict, items_description_with_language_code: dict
) -> dict:
    data["space_images"] = remove_duplicate_urls(data["space_images"])
    data['imagenes_rental_units'] = remove_duplicate_urls(data['imagenes_rental_units'])
    data["the_unit"] = remove_duplicate_urls(data["the_unit"])
    data["the_floor_plan"] = remove_duplicate_urls(data["the_floor_plan"])
    data["features"] = find_feature_keys(data["features"], feature_map)

    neighborhood, min_price, max_price, area_sqm, bedrooms = extract_features(
        data["Banner__features"]
    )

    data["neighborhood"] = neighborhood
    data["min_price"] = min_price
    data["max_price"] = max_price
    data["area_sqm"] = area_sqm
    data["bedrooms"] = bedrooms

    data['data_rental_unit'] = get_data_rental_unit(
        data["available"], 
        data["bathroom_square_meters"], 
        data["titles_rental_units"], 
        data['imagenes_rental_units']
    )
    data["space_images"] = get_all_imagenes(data["space_images"])

    data["Descriptions"] = get_all_descriptions(items_description_with_language_code)
    
    if data["tour_url"]:
        data["tour_url"] = data["tour_url"][0]

    return data

def get_data_rental_unit(
    availability_list: list, 
    amount_sqft_list: list, 
    titles_rental_units: list, 
    imagenes_rental_units: list
    ) -> list[dict]:
    result = []

    if not availability_list:
        return result.append({
                'calendario': '',
                'amount': '',
                'areaM2': '',
                'titulo': '',
                'images': '',})

    for index, available in enumerate(availability_list):
        entry = {
            'calendario': available,
            'amount': amount_sqft_list[index * 2],
            'areaM2': amount_sqft_list[index * 2 + 1],
            'titulo': titles_rental_units[index],
            'images': imagenes_rental_units,
        }
        result.append(entry)

    return result


def get_all_imagenes(space_images: list) -> list[dict]:
    all_imagenes = []

    if not space_images:
        return []
    for index, value in enumerate(space_images):
        cover = True if index == 0 else False
        all_imagenes.append(
            {
                "image": value,
                "isCover": cover,
            }
        )
    return all_imagenes


def get_all_descriptions(items_description_with_language_code: dict):
    all_descriptions = []
    dict_language = {
        1: "Propiedades",
        2: "Property",
    }
    for id_language, info_description in reversed(items_description_with_language_code.items()):
        info_description: list
        descriptions = {
            "LanguagesId": int(id_language) + 1 ,
            "title": "",
            "description": "",
        }
        try:
            descriptions["title"] = dict_language.get(descriptions["LanguagesId"])
            descriptions["description"] = info_description[1]["about_the_home"]
        except (IndexError, KeyError) as e:
            continue 
        
        if descriptions["description"]:
            all_descriptions.append(descriptions)

    return all_descriptions

def get_data_rental_unit(
    availability_list: list, 
    amount_sqft_list: list, 
    titles_rental_units: list, 
    imagenes_rental_units: list
    ) -> list[dict]:
    result = []
    if not availability_list:
        return result.append({
                'schedule': '',
                'amount': '',
                'areaM2': '',
                'title': '',
                'images': '',})
    for index, available in enumerate(availability_list):
        entry = {
            'schedule': available,
            'amount': amount_sqft_list[index * 2],
            'areaM2': amount_sqft_list[index * 2 + 1],
            'title': titles_rental_units[index],
            'images': imagenes_rental_units
        }
        result.append(entry)
    return result


def create_rental_units(
    property_data: Property, bedroom_count: int, rooms_data: List[RoomData]
) -> List[RentalUnits]:
    rental_units = []
    calendar_unit_list = []

    if bedroom_count < 1:
        bedroom_count = 1

    if rooms_data is None:
        rooms_data = []

    if not rooms_data:
        rooms_data = [RoomData(areaM2=int(property_data.areaM2), amount=0, schedule="Default", title="Default", images=[''])]  # Ajusta según los atributos de RoomData

    rooms_per_type = bedroom_count // len(rooms_data)

    for _, room_data in enumerate(rooms_data):
        for unit_index in range(rooms_per_type):
            reference_code = (
                f"{property_data.referenceCode}-{room_data.title}-{unit_index + 1:03}"
            )
            reference_code = re.sub(r'\s', '-', reference_code)
            rental_unit = RentalUnits(
                PropertyId=property_data.id,
                referenceCode=reference_code,
                areaM2=int(room_data.areaM2),
                Features=property_data.Features,
                isActive=True,
                isPublished=True,
                ContractsModels=[
                    ContractModel(
                        PropertyBusinessModelId=get_elements_types(
                            constants.MODELS_CONTRACT
                        ),
                        currency=CurrencyCode.EUR.value,
                        amount=int(room_data.amount),
                        depositAmount=constants.INT_ZERO,
                        reservationAmount=constants.INT_ZERO,
                        minPeriod=constants.INT_ONE,
                        paymentCycle=PaymentCycleEnum.MONTHLY.value,
                        extras=[],
                    )
                ],
                Descriptions=property_data.Descriptions,
                Images=get_all_imagenes(room_data.images),
            )

            rental_units.append(rental_unit)

    return rental_units


def get_default_values() -> dict:
    """
    Retorna un diccionario con los valores por defecto (hardcoded).
    """
    return {
        "cancellationPolicy": constants.CANCELLATION_POLICY,
        "rentalType": constants.RENTAL_TYPE,
        "isActive": constants.BOOL_TRUE,
        "isPublished": constants.BOOL_TRUE,
        "Languages": constants.LANGUAGES,
        "PropertyTypeId": get_elements_types(constants.PROPERTY_TYPE_ID), # 4
        "country": constants.COUNTRY,
        "countryCode": constants.COUNTRY_CODE,
    }


def save_data(data: dict) -> Property:

    defaults = get_default_values()

    property_item = Property(
        name=data["coliving_name"],
        description=data["Descriptions"][0]["description"],
        referenceCode=data["referenceCode"],
        areaM2=data["area_sqm"],
        rentalType=defaults["rentalType"],
        isActive=defaults["isActive"],
        isPublished=defaults["isPublished"],
        Features=data["features"],
        tourUrl=data["tour_url"],
        PropertyTypeId=defaults["PropertyTypeId"],
        Descriptions=[
            Description(
                LanguagesId=data_description["LanguagesId"],
                title=f'{data_description["title"]} {data["coliving_name"]}',
                description=data_description["description"],
            ).dict()
            for data_description in data["Descriptions"]
        ],
        Images=data["space_images"],
        Location=LocationAddress(
            lat=data["latitude"],
            lon=data["longitude"],
            country=defaults["country"],
            countryCode=defaults["countryCode"],
            city=data["city_name"],
        ),
    )
    #Property
    property_id = save_property(property_item)
    property_item.id = property_id
    create_json(property_item)

    #RentalUnits
    rooms_data = [
        RoomData(
            areaM2 = int(rental_unit['areaM2'].replace(" sqm", "")),
            amount=data["max_price"],
            schedule=rental_unit['schedule'],
            title=rental_unit['title'],
            images=rental_unit['images'],
        )
        for rental_unit in data['data_rental_unit']
    ]
    rental_units_items, calendar_unit_list = create_rental_units(
        property_item, 
        int(data["bedrooms"]), 
        rooms_data
    )
    list_rental_unit_id = []
    for unit in rental_units_items:
        rental_unit = save_rental_unit(unit)
        unit.id = rental_unit
        list_rental_unit_id.append(rental_unit)

    for unit in rental_units_items:
        create_json(unit)

    #schedule
    for rental_id, calendar_unit in zip(list_rental_unit_id, calendar_unit_list):
        check_and_insert_rental_unit_calendar(rental_id, calendar_unit)

    for calendar_unit in calendar_unit_list:
        create_json(calendar_unit)

def create_json(item: Union[RentalUnits, Property, DatePayloadItem]) -> None:
    class PathDocument(Enum):
        PROPERTY = "data/property.json"
        RENTAL_UNITS = "data/rental_units.json"
        CALENDAR = "data/calendar.json"

    current_dir = os.getcwd()

    if isinstance(item, RentalUnits):
        json_file_path = os.path.join(current_dir, PathDocument.RENTAL_UNITS.value)
    elif isinstance(item, Property):
        json_file_path = os.path.join(current_dir, PathDocument.PROPERTY.value)
    elif isinstance(item, DatePayloadItem):
        json_file_path = os.path.join(current_dir, PathDocument.CALENDAR.value)
    else:
        raise ValueError("item must be an instance of RentalUnits or Property or Calendar.")

    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)

    with open(json_file_path, "a", encoding="utf-8-sig") as json_file:
        json.dump(item.dict(), json_file, indent=4)

    logging.info(f"Datos guardados en: {json_file_path}")
