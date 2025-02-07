import json
import logging
import os
import re
import unicodedata
from collections import defaultdict
from enum import Enum
from os import path
from typing import List, Union

from pydantic import BaseModel
from scrapy import Spider

import app.models.enums as models
from app.config.settings import GlobalConfig, LOG_DIR, BASE_DIR
from app.models.enums import CurrencyCode, Languages, PaymentCycleEnum, feature_map
from app.models.schemas import (
    PriceItem,
    RentalUnitsCalendarItem,
    Text,
    LocationAddress,
    Property,
    RentalUnits,
    mapping,
)
from app.scrapy.common import get_all_imagenes, parse_elements, create_json
from app.scrapy.funcs import (
    check_and_insert_rental_unit_calendar,
    detect_language,
    find_feature_keys,
    get_elements_types,
    get_month_dates,
    save_property,
    save_rental_unit,
)

class RoomData(BaseModel):
    areaM2: int
    amount: int
    schedule: str
    title: str
    images: List[str]


def clean_string(text):
    cleaned_text = re.sub(r"\bBullones\b", "", text)
    cleaned_text = cleaned_text.replace("/", "")
    return cleaned_text.strip()


def remove_accents(text: str) -> str:
    normalized_text = unicodedata.normalize("NFD", text)
    return "".join(
        char for char in normalized_text if unicodedata.category(char) != "Mn"
    )


def get_all_descriptions(parse_description: list, parse_coliving_name: str):
    descriptions_dict = {
        "title_en": None,
        "description_en": None,
        "title_es": None,
        "description_es": None,
    }

    dict_language = {
        Languages.SPANISH.value: "Propiedades",
        Languages.ENGLISH.value: "Property",
    }

    for description in parse_description:
        lang_id = detect_language(description)
        if not lang_id:
            continue

        if lang_id == Languages.ENGLISH.value:
            descriptions_dict["title_en"] = f'{dict_language.get(lang_id, "")} {parse_coliving_name}'
            descriptions_dict["description_en"] = remove_accents(description)
        elif lang_id == Languages.SPANISH.value:
            descriptions_dict["title_es"] = f'{dict_language.get(lang_id, "")} {parse_coliving_name}'
            descriptions_dict["description_es"] = remove_accents(description)

    # Devolvemos el diccionario dentro de una lista
    return [descriptions_dict]


def create_rental_units(
    property_data: Property,
    bedroom_count: int,
    rooms_data: List[RoomData],
    elements_dict: dict,
) -> List[RentalUnits]:
    rental_units = []
    calendar_unit_list = []

    if bedroom_count < 1:
        bedroom_count = 1

    if rooms_data is None:
        rooms_data = []

    if not rooms_data:
        rooms_data = [
            RoomData(
                areaM2=int(property_data.areaM2),
                amount=0,
                schedule="Default",
                title="Default",
                images=[""],
            )
        ]  # Ajusta según los atributos de RoomData

    rooms_per_type = bedroom_count // len(rooms_data)

    for _, room_data in enumerate(rooms_data):
        for unit_index in range(rooms_per_type):
            reference_code = f"{room_data.title}-{unit_index + 1:03}"
            reference_code = re.sub(r"\s", "-", reference_code)
            rental_unit = RentalUnits(
                PropertyId=property_data.id,
                referenceCode=reference_code,
                areaM2=int(room_data.areaM2),
                Features=property_data.Features,
                isActive=True,
                isPublished=True,
                # ContractsModels=[
                #     ContractModel(
                #         PropertyBusinessModelId=get_elements_types(
                #             settings.MODELS_CONTRACT, elements_dict["contract_types"]
                #         ),
                #         currency=CurrencyCode.EUR.value,
                #         amount=int(room_data.amount),
                #         depositAmount=settings.INT_ZERO,
                #         reservationAmount=settings.INT_ZERO,
                #         minPeriod=settings.INT_ONE,
                #         paymentCycle=PaymentCycleEnum.MONTHLY.value,
                #         extras=[],
                #     )
                # ],
                Texts=property_data.Texts,
                Images=get_all_imagenes(room_data.images),
                Price=PriceItem(
                    contractType=PaymentCycleEnum.MONTHLY.value,
                    currency=CurrencyCode.EUR.value,
                    amount=int(room_data.amount),
                    depositAmount=int(room_data.amount),
                    reservationAmount=GlobalConfig.INT_ZERO,
                    minPeriod=GlobalConfig.INT_ONE,
                    paymentCycle=PaymentCycleEnum.MONTHLY.value
                ),
            )

            rental_units.append(rental_unit)
            # Calendar
            month_year = room_data.schedule.split("from")[-1].strip()
            start_date, end_date = get_month_dates(room_data.schedule)
            date_items = RentalUnitsCalendarItem(
                summary=f"Blocked until {month_year}",
                description=room_data.schedule,
                startDate=start_date,
                endDate=end_date,
            )
            calendar_unit_list.append(date_items)

    return rental_units, calendar_unit_list


def get_default_values(elements_dict) -> dict:
    """
    Retorna un diccionario con los valores por defecto (hardcoded).
    """
    return {
        "cancellationPolicy": GlobalConfig.CANCELLATION_POLICY,
        "rentalType": GlobalConfig.RENTAL_TYPE,
        "isActive": GlobalConfig.BOOL_TRUE,
        "isPublished": GlobalConfig.BOOL_TRUE,
        "Languages": GlobalConfig.LANGUAGES,
        "propertiesTypes": get_elements_types(
            GlobalConfig.PROPERTY_TYPE_ID, elements_dict["propertiesTypes"]
        ),  # 4
        "country": GlobalConfig.COUNTRY,
        "countryCode": GlobalConfig.COUNTRY_CODE,
    }


def parse_banner_features(banner_features):
    location = banner_features[0]

    price_info = banner_features[1]
    max_price = "".join(filter(str.isdigit, price_info.split("to")[-1]))
    currency = "".join(filter(str.isalpha, price_info.split()[1]))
    sqm = "".join(filter(str.isdigit, banner_features[2]))
    bedrooms = (
        int("".join(filter(str.isdigit, banner_features[3])))
        if len(banner_features) > 3
        else 1
    )

    return location, int(max_price), currency, int(sqm), int(bedrooms)

def generate_reference_code(city_name: str, coliving_name: str) -> str:
    """
    Genera un referenceCode basado en city_name y coliving_name.
    
    - Si la longitud total supera los 30 caracteres, usa solo coliving_name.
    - Agrega '-001' al final en ambos casos.

    Args:
        city_name (str): Nombre de la ciudad.
        coliving_name (str): Nombre del coliving.

    Returns:
        str: Código de referencia generado.
    """
    base_code = f"{city_name}-{coliving_name}-001"
    if len(base_code) > 30:
        return f"{coliving_name}-001"
    return base_code


class FlipcolivingPipeline:
    def open_spider(self, spider: Spider):
        spider.logger.info("open_spider")
        self.json_path = path.join(spider.output_folder, spider.output_filename)
        self.items = []
        self.elements_dict = parse_elements(spider.context, mapping)
        self.api_key = self.elements_dict["api_key"].data[0].name

    def process_item(self, item, spider: Spider):
        self.items.append(dict(item))
        # save lodgerin
        defaults = get_default_values(self.elements_dict)

        item = item["items_output"]
        _, _, _, areaM2, bedrooms = parse_banner_features(item["banner_features"])

        parse_coliving_name = remove_accents(item["parse_coliving_name"][0]).replace(
            " ", "-"
        )
        result_description = get_all_descriptions(
            item["parse_description"], parse_coliving_name
        )

        reference_code = generate_reference_code(item["city_name"], parse_coliving_name)

        try:
            property_item = Property(
                referenceCode=reference_code,
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
                PropertyTypeId=defaults["propertiesTypes"],
                Texts=result_description[0],
                Images=item.get("all_firts_imagenes", []),
                Location=LocationAddress(
                    lat=item["latitude"][0],
                    lon=item["longitude"][0],
                    country=defaults["country"],
                    countryCode=defaults["countryCode"],
                    city=item["city_name"],
                ),
            )

            property_id = save_property(property_item, self.api_key)
            property_item.id = property_id
            spider.logger.info(f"property_item creado con éxito: {property_item.id}")
            create_json(property_item)
            rooms_data = [
                RoomData(
                    areaM2=int(rental_unit["data_rental_unit"][1].replace(" sqm", "")),
                    amount=int(
                        rental_unit["data_rental_unit"][0]
                        .split(" to ")[-1]
                        .replace("€ /month", "")
                        .strip()
                    ),
                    schedule=rental_unit["available_rental_unit"][0],
                    title=clean_string(
                        remove_accents(
                            rental_unit["name_rental_unit"][0].replace(" ", "_")
                        )
                    ),
                    images=rental_unit["imagenes_rental_unit"],
                )
                for rental_unit in item["rental_units"]
            ]
            rental_units_items, calendar_unit_list = create_rental_units(
                property_item, int(bedrooms), rooms_data, self.elements_dict
            )
            list_rental_unit_id = []
            for unit in rental_units_items:
                rental_unit = save_rental_unit(unit, self.api_key)
                unit.id = rental_unit
                list_rental_unit_id.append(rental_unit)

            for unit in rental_units_items:
                create_json(unit)
            spider.logger.info(f"list_rental_unit_id {list_rental_unit_id}")

            # schedule
            for rental_id, calendar_unit in zip(
                list_rental_unit_id, calendar_unit_list
            ):
                check_and_insert_rental_unit_calendar(rental_id, calendar_unit, self.api_key)

            for calendar_unit in calendar_unit_list:
                create_json(calendar_unit)

            return property_item

        except Exception as e:
            spider.logger.error(f"Error al iniciar el scraping para {str(e)}")

    def close_spider(self, spider: Spider):
        spider.logger.info(f"close_spider {models.Pages.flipcoliving.value}")
        logging.info("close_spider - close_spider")
        with open(self.json_path, "w", encoding="utf-8") as json_file:
            json.dump(self.items, json_file, ensure_ascii=False, indent=4)
        spider.logger.info("Spider finished successfully")
