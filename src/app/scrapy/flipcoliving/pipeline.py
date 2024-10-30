import os
import re
import json
import ast
import logging
import calendar
from datetime import datetime
from typing import Union, List
from enum import Enum
from pydantic import BaseModel
from app.models.enums import feature_map
from app.models.schemas import (
    Property,
    RentalUnits,
    ContractModel,
    Description,
    Image,
    LocationAddress,
)
from app.utils.funcs import find_feature_keys



logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class RegexPatterns(str, Enum):
    RATE = r"[\d,.]+€"
    BEDROOMS = r"habitaciones|bedrooms"
    AREA_SQM = r"[Mm]2|[Ss][Qq][Mm]"
    NON_DIGITS = r"[^\d.,]+"


class RoomData(BaseModel):
    areaM2: str
    amount: str
    calendario: str
    titulo: str
    images: List[str]


def remove_duplicate_urls(url_list: list) -> list:
    cleaned_urls = []
    seen = set()

    for url in url_list:
        clean_url = re.sub(r"-\d+x\d+\.jpg", ".jpg", url.split()[0])
        clean_url = re.sub(r"-\d+x\d+\.pgn", ".pgn", url.split()[0])

        if clean_url not in seen:  # If the item has not been seen
            seen.add(clean_url)  # Add it to the set
            cleaned_urls.append(clean_url)  # Add it to the result list

    return cleaned_urls


def get_month_dates(text: str) -> tuple:
    """
    Extracts the month and year from a string and returns the start and end
    dates of the corresponding month in the "%Y-%m-%d" format.

    If the month is misspelled or the format is incorrect,
    it issues a warning and returns (None, None).

    Parameters:
    text (str): String in the format "Available from <Month> <Year>".

    Returns:
    tuple: Start and end dates of the month as strings in "%Y-%m-%d" format,
           or (None, None) if there is an error in the input.
    """

    try:
        # Extract month and year from the text
        date_str = text.replace("Available from ", "")
        date_obj = datetime.strptime(date_str, "%B %Y")

        # Get the last day of the month
        _, last_day = calendar.monthrange(date_obj.year, date_obj.month)

        # Create the start and end dates
        start_date = date_obj.replace(day=1).strftime("%Y-%m-%d")
        end_date = date_obj.replace(day=last_day).strftime("%Y-%m-%d")

        return start_date, end_date

    except ValueError:
        # Handle the case where the month or format is incorrect
        logger.error("Warning: The month or input format '%s' is incorrect.", text)
        return None, None


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
        logger.error("Failed to convert byte string to dictionary: %s", e)
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
            # print("rates:", rates)
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

    data["tour_url"] = str(data["tour_url"]) if data["tour_url"] else None

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
    for id_language, info_description in items_description_with_language_code.items():
        info_description: list
        # url_language = info_description[0]
        descriptions = {
            "LanguagesId": "",
            "title": "",
            "description": "",
        }
        descriptions["LanguagesId"] = id_language

        try:
            descriptions["description"] = info_description[1]["about_the_home"]
        except:
            pass

        if descriptions["description"] == "":
            continue

        all_descriptions.append(descriptions)

    return all_descriptions


def create_rental_units(property_data: Property, bedroom_count: int, rooms_data: List[RoomData]) -> List[RentalUnits]:
    rental_units = []
    
    if bedroom_count < 1:
        bedroom_count = 1

    if rooms_data is None:
        rooms_data = []

    if not rooms_data:
        #TODO: Ajustar valores
        rooms_data = [RoomData(areaM2=property_data.areaM2, amount=0, calendario="Default", titulo="Default", images=[''])]  # Ajusta según los atributos de RoomData

    rooms_per_type = bedroom_count // len(rooms_data)

    for _, room_data in enumerate(rooms_data):
        for unit_index in range(rooms_per_type):
            reference_code = f"{property_data.referenceCode}-{room_data.titulo}-{unit_index + 1:03}"
            reference_code = re.sub(r'\s', '-', reference_code)
            rental_unit = RentalUnits(
                PropertyId=property_data.id,
                referenceCode=reference_code,
                areaM2=room_data.areaM2,
                isActive=True,
                isPublished=True,
                ContractsModels=[
                    ContractModel(
                        PropertyBusinessModelId=1,
                        currency='USD',
                        amount=int(room_data.amount),
                        depositAmount=int(room_data.amount) * 2,
                        reservationAmount=0,
                        minPeriod=1,
                        paymentCycle="monthly",
                        extras=[],
                    )
                ],
                Descriptions=property_data.Descriptions,
                Images=get_all_imagenes(room_data.images)
            )
            
            rental_units.append(rental_unit)
    
    return rental_units


def get_imagenes_rental_units(imagenes_rental_units: list):
    
    aux_imagenes_rental_units, imagenes_rental_units = imagenes_rental_units, []
    for value in aux_imagenes_rental_units:
        value: str
        if not value.endswith('.jpg'):
            continue
        imagenes_rental_units.append(value)
    
    return imagenes_rental_units

def get_default_values() -> dict:
    """
    Retorna un diccionario con los valores por defecto (hardcoded).
    """
    return {
        "cancellationPolicy": "standard",
        "rentalType": "individual",
        "isActive": True,
        "isPublished": True,
        "Languages": [1, 2],
        "videoUrl": "",
        "tourUrl": "",
        "PropertyTypeId": 4,  # Coliving
        "Images": [
            {
                "image": "https://lodgerin-archives-production.s3.amazonaws.com/uploads/archive/name/34564/10.jpg",
                "isCover": True,
            },
            {
                "image": "https://lodgerin-archives-production.s3.amazonaws.com/uploads/archive/name/34564/10.jpg",
                "isCover": False,
            },
            {
                "image": "https://lodgerin-archives-production.s3.amazonaws.com/uploads/archive/name/34564/10.jpg",
                "isCover": False,
            },
        ],
        "country": "Spain",
        "countryCode": "ES",
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
        videoUrl=defaults["videoUrl"],
        tourUrl=data["tour_url"],
        PropertyTypeId=defaults["PropertyTypeId"],
        Descriptions=[
            Description(
                LanguagesId=data_description["LanguagesId"],
                title=data_description["title"],
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
    
    #TODO: create_property(property_item)

    rooms_data = [
        RoomData(
            areaM2=rental_unit['areaM2'],
            amount=data["max_price"],
            calendario=rental_unit['calendario'],
            titulo=rental_unit['titulo'],
            images=rental_unit['images'],
        )
        for rental_unit in data['data_rental_unit']
    ]

    rental_units_items = create_rental_units(
        property_item, 
        int(data["bedrooms"]), 
        rooms_data
    )
    create_json(property_item)
    for unit in rental_units_items:
        create_json(unit)


def create_json(item: Union[RentalUnits, Property]) -> None:
    class PathDocument(Enum):
        RENTAL_UNITS = "data/rental_units.json"
        PROPERTY = "data/output_document.json"

    current_dir = os.getcwd()

    if isinstance(item, RentalUnits):
        json_file_path = os.path.join(current_dir, PathDocument.RENTAL_UNITS.value)
    elif isinstance(item, Property):
        json_file_path = os.path.join(current_dir, PathDocument.PROPERTY.value)
    else:
        raise ValueError("item must be an instance of RentalUnits or Property.")

    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)

    with open(json_file_path, "a", encoding="utf-8-sig") as json_file:
        json.dump(item.dict(), json_file, indent=4)

    print(f"Datos guardados en: {json_file_path}")
