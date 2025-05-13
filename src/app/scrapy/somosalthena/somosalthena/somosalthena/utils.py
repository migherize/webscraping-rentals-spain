import calendar
import json
import re
from asyncio import constants
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, Type

from pydantic import BaseModel, Field
from scrapy import Spider

import app.config.settings as settings
import app.scrapy.funcs as funcs
from app.models.enums import CurrencyCode, PaymentCycleEnum
from app.models.schemas import Property, RentalUnits, PriceItem
from app.scrapy.common import clean_information_html, get_all_images, get_id_from_name, search_feature_with_map, extract_id_label
from app.models.features_spider import FeaturesSomosAlthena

class PropertyTypeColiving(Enum):
    PROPERTY_TYPE = (
        "Pisos",
        "Casas",
        "Edificios",
    )
    OPERATION = "alquiler"


def get_data_json(json_path_no_refined: str) -> list[dict]:
    """
    object_spider:
        keys:
            "output_folder_path"
            "output_folder_name"
            "file_name"
            "processed_name"
            "refine"
            "output_folder"
    """

    output_data = []

    # Leer un archivo JSON
    with open(json_path_no_refined, "r") as file:
        all_data = json.load(file)
        for data_json in all_data:
            if not data_json:
                continue
            if not (
                data_json["GrupoInmueble"] in PropertyTypeColiving.PROPERTY_TYPE.value
            ):
                continue
            if not (data_json["Operacion"] == PropertyTypeColiving.OPERATION.value):
                continue
            refined_data_json = refine_data_json(data_json)
            output_data.append(refined_data_json)

    return output_data


def refine_data_json(data_json: dict) -> dict:

    output_json_data = {
        "title": "",
        "referend_code": "",
        "cost": "",
        "area_building": "",
        "area_utils": "",
        "bedrooms": "",
        "bathrooms": "",
        "all_titles": {
            "spanish": "",
            "catalan": "",
            "english": "",
            "french": "",
        },
        "all_descriptions_short": {
            "spanish": "",
            "catalan": "",
            "english": "",
            "french": "",
        },
        "all_descriptions": {
            "spanish": "",
            "catalan": "",
            "english": "",
            "french": "",
        },
        "address": {
            "Numero": "",
            "Direccion": "",
            "Zona": "",
            "Provincia": "",
            "Poblacion": "",
            "CodigoPostal": "",
            "latitude": "",
            "longitude": "",
        },
        "images": [],
        "features": [],
        "GrupoInmueble": "",
        "Operacion": "",
    }

    output_json_data["GrupoInmueble"] = data_json["GrupoInmueble"]
    output_json_data["Operacion"] = data_json["Operacion"]

    output_json_data["title"] = data_json["Titulo"]
    output_json_data["referend_code"] = data_json["Referencia"]
    output_json_data["cost"] = data_json["Precio"]
    output_json_data["area_building"] = data_json["MetrosConstruidos"]
    output_json_data["area_utils"] = data_json["MetrosUtiles"]

    output_json_data["bedrooms"] = data_json["Habitaciones"]
    output_json_data["bathrooms"] = data_json["Banos"]

    output_json_data["address"]["Numero"] = data_json["Numero"]
    output_json_data["address"]["Direccion"] = data_json["Direccion"]
    output_json_data["address"]["Zona"] = data_json["Zona"]
    output_json_data["address"]["Provincia"] = data_json["Provincia"]
    output_json_data["address"]["Poblacion"] = data_json["Poblacion"]
    output_json_data["address"]["CodigoPostal"] = data_json["CodigoPostal"]
    output_json_data["address"]["latitude"] = data_json["Latitud"]
    output_json_data["address"]["longitude"] = data_json["Longitud"]

    output_json_data["output_address"] = get_address(output_json_data["address"])

    all_titles = ("Titulo", "TituloCa", "TituloEn", "TituloFr")
    output_json_data = get_all_multidata(
        all_titles, data_json, output_json_data, "all_titles"
    )

    all_description = (
        "DescripcionAmpliada",
        "DescripcionAmpliadaCa",
        "DescripcionAmpliadaEn",
        "DescripcionAmpliadaFr",
    )
    output_json_data = get_all_multidata(
        all_description, data_json, output_json_data, "all_descriptions"
    )

    all_description_short = (
        "Descripcion",
        "DescripcionCa",
        "DescripcionEn",
        "DescripcionFr",
    )
    output_json_data = get_all_multidata(
        all_description_short, data_json, output_json_data, "all_descriptions_short"
    )
    output_json_data["images"] = get_all_images(data_json["Fotos"])
    output_json_data["features"] = get_all_features(data_json)
    return output_json_data


def get_address(address: dict) -> dict:
    aux_address = {
        "number": address["Numero"],
        "lat": address["latitude"],
        "lon": address["longitude"],
        "fullAddress": "",
        "address": "",
        "city": address["Poblacion"],
        "street": address["Direccion"],
        "state": address["Provincia"],
        "postalCode": address["CodigoPostal"],
        "country": "",
        "countryCode": "",
        "prefixPhone": "",
    }
    aux_address["address"] = (
        f"{aux_address['number']} "
        f"{aux_address['street']}, "
        f"{aux_address['city']}, "
        f"{aux_address['state']}, "
        f"{aux_address['postalCode']}"
    )
    aux_address["address"] = re.sub(r"\s{2,}", " ", aux_address["address"])
    aux_address["fullAddress"] = aux_address["address"]
    return aux_address

def get_all_multidata(
    multidata: tuple[str],
    data_json: dict,
    output_json_data: dict,
    key_main: str,
):
    for data, key_data_json in zip(multidata, output_json_data[key_main].keys()):
        output_json_data[key_main][key_data_json] = clean_information_html(
            data_json[data]
        )

    return output_json_data


def get_all_features(data_json: dict):

    all_feature_somosalthena = FeaturesSomosAlthena.FEATURES
    invalid_values = {0, "0", "", None, "None"}
    output_info_feature = {
        feature: True
        for feature in all_feature_somosalthena
        if data_json.get(feature) not in invalid_values
    }
    return output_info_feature

def process_descriptions_with_fallback(
    all_descriptions: dict,
    all_titles: dict,
    all_descriptions_short: dict,
) -> dict:
    """
    Procesa títulos y descripciones en español e inglés y devuelve un diccionario con formato estándar.

    :param all_descriptions: Diccionario de descripciones largas por idioma.
    :param all_titles: Diccionario de títulos por idioma.
    :param all_descriptions_short: Diccionario de descripciones cortas por idioma.
    :return: Diccionario con títulos y descripciones en español e inglés.
    """

    language_map = {
        "spanish": "es",
        "english": "en"
    }

    result = {
        "title_en": "None",
        "title_es": "None",
        "description_en": "None",
        "description_es": "None",
    }

    for lang_key, lang_code in language_map.items():
        title = all_titles.get(lang_key, "").strip()
        description = all_descriptions.get(lang_key, "").strip()
        description_short = all_descriptions_short.get(lang_key, "").strip()
        final_description = description if description else description_short
        if title:
            result[f"title_{lang_code}"] = title
        if final_description:
            result[f"description_{lang_code}"] = final_description
    return result


def process_descriptions(
    all_descriptions: dict, all_titles: dict, languages_dict: dict
) -> list:
    """
    Procesa las descripciones en varios idiomas y devuelve una lista de diccionarios con el ID del idioma.

    Args:
        all_descriptions (dict): Diccionario con las descripciones en diferentes idiomas.
        languages_dict (dict): Diccionario con la lista de idiomas.

    Returns:
        list: Lista de diccionarios con el formato deseado, con ID de idioma y las descripciones.
    """
    result = []

    for (lang_key_desc, description), (lang_key_title, title) in zip(
        all_descriptions.items(), all_titles.items()
    ):
        if lang_key_desc == lang_key_title:
            language_id = get_id_from_name(
                languages_dict, lang_key_desc.capitalize(), "name_en"
            )
            if language_id and title and description:
                result.append(
                    {
                        "LanguagesId": language_id,
                        "title": title,
                        "description": description,
                    }
                )
    return result

def retrive_lodgerin_property(items, elements):
    PropertyTypeId = get_id_from_name(
        elements["propertiesTypes"].data, "Apartment / Entire flat", "name_en"
    )
    descriptions = process_descriptions_with_fallback(
        items["all_descriptions"],
        items["all_titles"],
        items["all_descriptions_short"],
    )

    element_feature = extract_id_label(elements["features"].data)
    features_id = search_feature_with_map(
        items["features"],
        element_feature,
        FeaturesSomosAlthena.FEATURES,
    )

    property_items = Property(
        referenceCode=items["referend_code"],
        areaM2=items["area_building"],
        areaM2Available=float(items["area_utils"]) if float(items["area_utils"]) != 0 else 1,
        cancellationPolicy=settings.GlobalConfig.CANCELLATION_POLICY,
        rentalType=settings.GlobalConfig.RENTAL_TYPE,
        isActive=True,
        isPublished=True,
        Features=features_id,
        PropertyTypeId=PropertyTypeId,
        Texts=descriptions,
        Images=items["images"],
        Location=items["output_address"],
        provider="somosalthena",
        providerRef=items["referend_code"],
        # Languages=language_ids,
    )

    return property_items, items["cost"]


def retrive_lodgerin_rental_units(
    items_property: Property, elements_dict: dict, cost: str
):
    
    data_rental_units = RentalUnits(
        Images=items_property.Images,
        PropertyId=items_property.id,
        referenceCode=f"{items_property.referenceCode}-001",
        areaM2=items_property.areaM2,
        areaM2Available=float(items_property.areaM2Available),
        isActive=True,
        isPublished=True,
        Price=PriceItem(
            contractType=PaymentCycleEnum.MONTHLY.value,
            currency=CurrencyCode.EUR.value,
            amount=float(cost),
            depositAmount=float(cost),
            reservationAmount=settings.GlobalConfig.INT_ZERO,
            minPeriod=settings.GlobalConfig.INT_ONE,
            paymentCycle=PaymentCycleEnum.MONTHLY.value
        ),
        Texts=items_property.Texts,
    )

    return data_rental_units


def get_month() -> tuple:
    now = datetime.now()
    start_date = now.replace(day=1)
    next_month = now.replace(day=28) + timedelta(days=4)
    end_date = next_month.replace(day=1) - timedelta(days=1)
    month_name = calendar.month_name[now.month]

    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")

    return start_date_str, end_date_str, month_name


def parse_elements(
    full_json: Dict, mapping: Dict[str, Type[BaseModel]]
) -> Dict[str, dict]:
    """
    Procesa un JSON completo y lo convierte en un diccionario con clases Pydantic.

    Args:
        full_json (dict): El JSON que contiene los datos para procesar.
        mapping (dict): Un mapeo de nombres de claves a clases Pydantic.

    Returns:
        dict: Un diccionario con los datos parseados.
    """
    elements_dict = {}
    for key, model_class in mapping.items():
        if key in full_json:
            elements_dict[key] = model_class(**full_json[key]).dict()
        else:
            raise KeyError(f"Key '{key}' not found in the provided JSON")
    return elements_dict