from asyncio import constants
import re
import json
from scrapy import Spider
from enum import Enum
from app.scrapy.common import clean_information_html, get_all_images
from app.models.schemas import Property, RentalUnits
import app.utils.constants as constants
import app.utils.funcs as funcs
from app.models.schemas import (
    Property,
    RentalUnits,
    ContractModel,
)
from app.models.enums import CurrencyCode, PaymentCycleEnum
from datetime import datetime, timedelta
import calendar
from typing import Dict, Any, Type
from pydantic import BaseModel, Field

class PropertyTypeColiving(Enum):
    PROPERTY_TYPE = (
        'Pisos',
        'Casas',
        'Edificios',
    )
    OPERATION = 'alquiler'

class FeaturesSomosAlthena(Enum):

    FEATURES = {
        "Habitaciones",
        "Cocina",
        "Trasteros",
        "Altillo",
        "ZonasComunes",
        "Terrazas",
        "Gas",
        "AccesoDiscapacitados",
        "Agua",
        "AdmiteMascotas",
        "Microondas",
        "Vigilancia24h",
        "PiscinaPrivada",
        "SofaCama",
        "Sillas",
        "AireAcondicionado",
        "Despachos",
        "CocinaAmueblada",
        "Chimeneas",
        "Amueblado",
        "Exterior",
        "Televisor",
        "CajaFuerte",
        "Conserje",
        "Luz",
        "Ascensor",
        "Alarma",
        "Cama",
        "Calefaccion",
        "Internet",
        "Banos",
        "ZonaInfantil",
        "Armarios",
        "Mesa",
        "Lavadero",
        "Horno",
    }
    EQUIVALENCES_FEATURES = {
        # "Habitaciones": "Bedroom lock",
        "Banos": "Private bath",
        "AireAcondicionado": "Air conditioning",
        "Exterior": "Exterior",
        "Internet": "Wi-fi",
        "Cocina": "Kitchen",
        "PiscinaPrivada": "Swimming pool",
        "AdmiteMascotas": "Pets allowed",
        "Calefaccion": "Heating system",
        "Ascensor": "Lift",
        "Conserje": "24hr Concierge Reception",
        "Alarma": "Smoke alarm",
        "Vigilancia24h": "Video surveillance",
        "AccesoDiscapacitados": "Wheelchair access",
        "ZonaInfantil": "Playground",
        "Terrazas": "Terrace / balcony",
        "Gas": "Gas",
        "Agua": "Water",
        "Luz": "Electricity",
        "Amueblado": "Furnished",
        "ZonasComunes": "Common areas",
    }
    EQUIVALENCES_FURNITURES = {
        "Armarios": "Wardrobe",
        "CocinaAmueblada": "Fitted wardrobes",
        "Lavadero": "Washer",
        "CajaFuerte": "Closet",
        "Mesa": "Desk",
        "Sillas": "Chair",
        "Televisor": "Television",
        "Cama": "Double bed",
        "SofaCama": "Futon",
        "Horno": "Oven",
        "Microondas": "Microwave",
        "Trasteros": "Extra storage",
        "Despachos": "Filing Cabinet",
        "Altillo": "Bookshelf/Bookcase",
        # "Chimeneas": "Iron"
    }

class PropertyTypeColiving(Enum):
    PROPERTY_TYPE = (
        'Pisos',
        'Casas',
        'Edificios',
    )
    OPERATION = 'alquiler'


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
            if not (data_json['GrupoInmueble'] in PropertyTypeColiving.PROPERTY_TYPE.value):
                continue
            if not (data_json['Operacion'] == PropertyTypeColiving.OPERATION.value):
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
        "GrupoInmueble":"",
        "Operacion":"",
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

    all_feature_somosalthena = FeaturesSomosAlthena.FEATURES.value
    invalid_values = {0, "0", "", None, "None"}
    output_info_feature = {
        feature: True
        for feature in all_feature_somosalthena
        if data_json.get(feature) not in invalid_values
    }
    return output_info_feature


def extract_id_name(data):
    # data = features_json.get("features", {}).get("data", [])
    return {item["id"]: item["name"] for item in data}


def get_id_from_name(data_dict: dict, name: str, key_name: str) -> int:
    """
    Busca el ID asociado a un nombre en un diccionario con estructura similar a "property_types" o "pension_types".

    Args:
        data_dict (dict): Diccionario que contiene una lista de datos bajo la llave "data".
        name (str): Nombre que se desea buscar.

    Returns:
        int: El ID asociado al nombre, si se encuentra. De lo contrario, retorna None.
    """
    for item in data_dict.get("data", []):
        if item.get(key_name) == name:
            return item.get("id")
    return None

def process_descriptions_with_fallback(
    all_descriptions: dict,
    all_titles: dict,
    all_descriptions_short: dict,
    languages_dict: dict,
) -> tuple:
    result = []
    language_ids = []

    for lang_key in all_titles.keys():
        title = all_titles.get(lang_key, "").strip()
        description = all_descriptions.get(lang_key, "").strip()
        description_short = all_descriptions_short.get(lang_key, "").strip()

        final_description = description if description else description_short

        if title and final_description:
            language_id = get_id_from_name(
                languages_dict, lang_key.capitalize(), "name_en"
            )
            if language_id:
                result.append(
                    {
                        "LanguagesId": language_id,
                        "title": title,
                        "description": final_description,
                    }
                )
                language_ids.append(language_id)

    return result, language_ids

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


def search_feature_with_map(
    items_features: dict, elements_features: dict, equivalences: dict
):

    true_ids = []

    for item_feature, status in items_features.items():
        if status:
            if item_feature in equivalences:
                mapped_feature = equivalences[item_feature]
                element_id = next(
                    (
                        id_
                        for id_, name in elements_features.items()
                        if name == mapped_feature
                    ),
                    None,
                )
                if element_id is not None:
                    true_ids.append(element_id)

    return true_ids


def retrive_lodgerin_property(items, elements):
    PropertyTypeId = get_id_from_name(elements["property_types"], "Studio/Entire flat", "name")
    descriptions, language_ids = process_descriptions_with_fallback(
        items["all_descriptions"],
        items["all_titles"],
        items["all_descriptions_short"],
        elements["languages"],
    )

    element_feature = extract_id_name(elements['features']['data'])
    features_id = search_feature_with_map(items['features'], element_feature, FeaturesSomosAlthena.EQUIVALENCES_FEATURES.value)
    
    property_items = Property(
        referenceCode=items["referend_code"],
        areaM2=items["area_building"],
        areaM2Available=items["area_utils"] if float(items["area_utils"]) != 0 else 1,
        cancellationPolicy=constants.CANCELLATION_POLICY,
        rentalType=constants.RENTAL_TYPE,
        isActive=True,
        isPublished=True,
        Features=features_id,
        PropertyTypeId=PropertyTypeId,
        Descriptions=descriptions,
        Images=items["images"],
        Location=items["output_address"],
        provider="somosalthena",
        providerRef=items["referend_code"],
        Languages=language_ids
    )

    return property_items, items["cost"]

def retrive_lodgerin_rental_units(items_property: Property,elements_dict: dict, cost: str):
    data_rental_units = RentalUnits(
    PropertyId=items_property.id,
    referenceCode=f'{items_property.referenceCode}-001',
    areaM2=items_property.areaM2,
    areaM2Available=float(items_property.areaM2Available),
    isActive=True,
    isPublished=True,
    ContractsModels=[ContractModel(
        PropertyBusinessModelId=funcs.get_elements_types(
            constants.MODELS_CONTRACT,elements_dict['contract_types']
        ),
        currency=CurrencyCode.EUR.value,
        amount=float(cost),
        depositAmount=float(cost),
        reservationAmount=constants.INT_ZERO,
        minPeriod=constants.INT_ONE,
        paymentCycle=PaymentCycleEnum.MONTHLY.value,
        extras=[],
    )],
    Descriptions=items_property.Descriptions,
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

def parse_elements(full_json: Dict, mapping: Dict[str, Type[BaseModel]]) -> Dict[str, dict]:
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
