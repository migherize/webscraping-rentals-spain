# -*- coding: utf-8 -*-

import json
import os
import re
from os import path
import logging
from collections import defaultdict
from .constants_spider import spider_names
from pydantic import BaseModel
import unicodedata
from enum import Enum
from typing import Union, List
import app.utils.constants as constants
from app.models.enums import feature_map, CurrencyCode, PaymentCycleEnum, Languages
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
import app.models.enums as models
from app.utils.funcs import find_feature_keys, get_elements_types, save_property, save_rental_unit,get_month_dates,check_and_insert_rental_unit_calendar,detect_language


os.makedirs(constants.LOG_DIR, exist_ok=True)
print(f"Log directory: {constants.LOG_DIR}") 

spider_logger = logging.getLogger("scrapy_spider")
spider_logger.setLevel(logging.DEBUG)

if not spider_logger.handlers:
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler = logging.FileHandler(
        os.path.join(constants.LOG_DIR, f"{models.Pages.flipcoliving.value}.log"),
        mode="a",
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    spider_logger.addHandler(file_handler)

print(f"Iniciando la pipeline '{models.Pages.flipcoliving.value}'.log")
class RoomData(BaseModel):
    areaM2: int
    amount: int
    schedule: str
    title: str
    images: List[str]

def clean_string(text):
    cleaned_text = re.sub(r'\bBullones\b', '', text)
    cleaned_text = cleaned_text.replace("/", "")
    return cleaned_text.strip()


def remove_accents(text: str) -> str:
    normalized_text = unicodedata.normalize('NFD', text)
    return ''.join(char for char in normalized_text if unicodedata.category(char) != 'Mn')

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



def get_all_descriptions(parse_description: list, parse_coliving_name:str):
    all_descriptions = []
    dict_language = {
        Languages.SPANISH.value: "Propiedades",
        Languages.ENGLISH.value: "Property",
    }
    
    for description in parse_description:
        lang_id = detect_language(description)
        if not lang_id:
            continue
        
        descriptions = {
            "LanguagesId": lang_id,
            "title": f'{dict_language.get(lang_id, "")} {parse_coliving_name}',
            "description": remove_accents(description),
        }
        
        if descriptions["description"]:
            all_descriptions.append(descriptions)

    return all_descriptions

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
                f"{room_data.title}-{unit_index + 1:03}"
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
            # Calendar
            month_year = room_data.schedule.split("from")[-1].strip()
            start_date, end_date = get_month_dates(room_data.schedule)
            date_items=DatePayloadItem(
                summary= f"Blocked until {month_year}",
                description= room_data.schedule,
                startDate= start_date,
                endDate= end_date,
            )
            calendar_unit_list.append(date_items)

    return rental_units, calendar_unit_list


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
        "PropertyTypeId": get_elements_types(constants.PROPERTY_TYPE_ID),  # 4
        "country": constants.COUNTRY,
        "countryCode": constants.COUNTRY_CODE,
    }



def parse_banner_features(banner_features):
    location = banner_features[0]

    price_info = banner_features[1]
    max_price = "".join(filter(str.isdigit, price_info.split("to")[-1]))
    currency = "".join(filter(str.isalpha, price_info.split()[1]))
    sqm = "".join(filter(str.isdigit, banner_features[2]))
    bedrooms = int("".join(filter(str.isdigit, banner_features[3]))) if len(banner_features) > 3 else 1

    return location, int(max_price), currency, int(sqm), int(bedrooms)

def merge_by_language(descriptions):
    merged = defaultdict(lambda: {"LanguagesId": None, "title": "", "description": ""})

    for item in descriptions:
        lang_id = item["LanguagesId"]

        if merged[lang_id]["LanguagesId"] is None:
            merged[lang_id]["LanguagesId"] = lang_id
            merged[lang_id]["title"] = item["title"]

        merged[lang_id]["description"] += (item["description"] + ". ")

    return [dict(value) for value in merged.values()]

class FlipcolivingPipeline:
    def open_spider(self, spider):
        self.json_path = path.join(spider.output_folder, spider.output_filename)
        self.items = []

    def process_item(self, item, spider):
        self.items.append(dict(item))
        print("entre a guardar")
        # save lodgerin
        defaults = get_default_values()
        item = item["items_output"]
        neighborhood, amount, currency, areaM2, bedrooms = parse_banner_features(
            item["banner_features"]
        )

        parse_coliving_name = remove_accents(item["parse_coliving_name"][0]).replace(" ", "-")
        result_description = get_all_descriptions(item["parse_description"],parse_coliving_name)
        result_description = merge_by_language(result_description)
        print(f"result_description {result_description}")

        try:
            property_item = Property(
                name=parse_coliving_name,
                description=item["parse_description"][0],
                referenceCode=f'{item["city_name"]}-{parse_coliving_name}-001',
                areaM2=areaM2,
                rentalType=defaults["rentalType"],
                isActive=defaults["isActive"],
                isPublished=defaults["isPublished"],
                Features=find_feature_keys(item["all_features"], feature_map),
                tourUrl=(
                    item["tour_url"][0]
                    if "tour_url" in item and item["tour_url"]
                    else None
                ),
                PropertyTypeId=defaults["PropertyTypeId"],
                Descriptions=[
                    Description(
                        LanguagesId=data_description["LanguagesId"],
                        title=data_description["title"],
                        description=data_description["description"],
                    ).dict()
                    for data_description in result_description
                ],
                Images=item.get("all_firts_imagenes", []),
                Location=LocationAddress(
                    lat=item["latitude"][0],
                    lon=item["longitude"][0],
                    country=defaults["country"],
                    countryCode=defaults["countryCode"],
                    city=item["city_name"],
                ),
            )

            print(f"property_item creado con éxito: {property_item}")
            property_id = save_property(property_item)
            property_item.id = property_id
            create_json(property_item)

            rooms_data = [
                RoomData(
                    areaM2=int(rental_unit['data_rental_unit'][1].replace(" sqm", "")),
                    amount=int(rental_unit['data_rental_unit'][0].split(" to ")[-1].replace("€ /month", "").strip()),
                    schedule=rental_unit['available_rental_unit'][0],
                    title=clean_string(remove_accents(rental_unit['name_rental_unit'][0].replace(" ", "_"))), 
                    images=rental_unit['imagenes_rental_unit'], 
                )
                for rental_unit in item['rental_units']
            ]
            rental_units_items, calendar_unit_list = create_rental_units(
                    property_item, 
                    int(bedrooms), 
                    rooms_data
                )
            list_rental_unit_id = []
            for unit in rental_units_items:
                rental_unit = save_rental_unit(unit)
                unit.id = rental_unit
                list_rental_unit_id.append(rental_unit)

            for unit in rental_units_items:
                create_json(unit)
            print(f'list_rental_unit_id {list_rental_unit_id}')
            
            #schedule
            for rental_id, calendar_unit in zip(list_rental_unit_id, calendar_unit_list):
                check_and_insert_rental_unit_calendar(rental_id, calendar_unit)

            for calendar_unit in calendar_unit_list:
                create_json(calendar_unit)

            return property_item

        except Exception as e:
            print(f"Error al iniciar el scraping para {str(e)}")

    def close_spider(self, spider):
        print(f"close_spider {models.Pages.flipcoliving.value}")
        with open(self.json_path, "w", encoding="utf-8") as json_file:
            json.dump(self.items, json_file, ensure_ascii=False, indent=4)
        print("Spider finished successfully")