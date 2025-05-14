import re
import unicodedata
from typing import List
from logging import Logger
from pydantic import BaseModel

from app.config.settings import GlobalConfig
from app.models.enums import CurrencyCode, Languages, Pages, PaymentCycleEnum, feature_map

from app.scrapy.common import (
    parse_elements, 
    get_all_imagenes, 
    create_json, 
    create_rental_unit_code_with_initials,
    read_json

)
from app.models.schemas import (
    PriceItem,
    RentalUnitsCalendarItem,
    LocationAddress,
    Property,
    RentalUnits,
    mapping
)
from app.scrapy.funcs import (
    check_and_insert_rental_unit_calendar,
    detect_language,
    find_feature_keys,
    get_elements_types,
    get_month_dates,
    save_property,
    save_rental_unit,
)
from app.scrapy.common import remove_accents, search_feature_with_map, extract_id_label, filtrar_ids_validos
from app.models.features_spider import EquivalencesFlipColinving
from app.services.csvexport import CsvExporter


class RoomData(BaseModel):
    areaM2: int
    amount: int
    schedule: str
    title: str
    images: List[str]


def etl_data_flipcoliving(output_path: list[dict], logger: Logger, context) -> None:

    items: list[dict[str, str]] = read_json(output_path)

    if items == []:
        logger.warning('- La data se encuentra vacia')
        return None

    elements_dict = parse_elements(context, mapping)
    api_key = elements_dict["api_key"].data[0].name
    
    for index, item in enumerate(items):
        try:
            flip_coliving = ETLFlipColiving(elements_dict, api_key)
            flip_coliving.parse_data(item, logger)
        except Exception as error:
            logger.error('error en el item numero %s', index)
            logger.error('error: %s', error)


class ETLFlipColiving:

    def __init__(self, elements_dict: str, api_key: str) -> None:
        self.elements_dict = elements_dict 
        self.api_key = api_key

    def save_data_property(self):
        pass

    def save_data_rental_unit(self):
        pass

    def parse_data(self, item: dict, logger: Logger) -> None:
        defaults = get_default_values(self.elements_dict)
        item = item["items_output"]
        _, _, _, areaM2, bedrooms = parse_banner_features(item["banner_features"])
        parse_coliving_name = remove_accents(item["parse_coliving_name"][0]).replace(" ", "-")
        result_description = get_all_descriptions(item["parse_description"], parse_coliving_name)
        reference_code = generate_reference_code(item["city_name"], parse_coliving_name)
        exporter = CsvExporter(Pages.flipcoliving.value)
            
        element_feature = extract_id_label(self.elements_dict["features"].data)
        features_id = search_feature_with_map(
            item["all_features"],
            element_feature,
            EquivalencesFlipColinving.FEATURES,
        )

        try:
            property_item = Property(
                referenceCode=reference_code,
                areaM2=areaM2,
                rentalType=defaults["rentalType"],
                isActive=defaults["isActive"],
                isPublished=defaults["isPublished"],
                Features=features_id,
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
            create_json(property_item, Pages.flipcoliving.value)
            rooms_data = [
                RoomData(
                    areaM2=int(float(rental_unit["data_rental_unit"][1].replace(" sqm", "").replace(",", ".").strip())),
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
                property_item, int(bedrooms), rooms_data, self.elements_dict, parse_coliving_name
            )

            list_rental_unit_id = []
            for unit in rental_units_items:
                rental_unit = save_rental_unit(unit, self.api_key)
                unit.id = rental_unit
                list_rental_unit_id.append(rental_unit)

            for unit in rental_units_items:
                create_json(unit, Pages.flipcoliving.value)
                exporter.process_and_export_to_csv(property_item, unit)
            
            # schedule
            for rental_id, calendar_unit in zip(
                list_rental_unit_id, calendar_unit_list
            ):
                if calendar_unit.startDate in ("None", None):
                    continue
                check_and_insert_rental_unit_calendar(rental_id, calendar_unit, self.api_key)

            for calendar_unit in calendar_unit_list:
                create_json(calendar_unit, Pages.flipcoliving.value)

            return property_item

        except Exception as e:
            logger.error(f"Error al iniciar el scraping para {str(e)}")


def clean_string(text: str) -> str:
    """Limpia la cadena eliminando la palabra 'Bullones' y los caracteres '/'."""
    return re.sub(r"\bBullones\b", "", text).replace("/", "").strip()


def get_all_descriptions(parse_description: list, parse_coliving_name: str):
    descriptions_dict = {
        "title_en": "None",
        "description_en": "None",
        "title_es": "None",
        "description_es": "None",
    }

    dict_language = {
        Languages.SPANISH.value: "Propiedades",
        Languages.ENGLISH.value: "Property",
    }

    for description in parse_description:
        if not description:
            continue

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
    parse_coliving_name: str,
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
            reference_code = create_rental_unit_code_with_initials(
                property_data.referenceCode, unit_index
            )
            rental_unit = RentalUnits(
                PropertyId=property_data.id,
                referenceCode=reference_code,
                areaM2=int(room_data.areaM2),
                isActive=True,
                isPublished=True,
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
                ExtraFeatures=filtrar_ids_validos(property_data.Features)
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

