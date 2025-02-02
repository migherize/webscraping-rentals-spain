import json
import re
from typing import Dict, Type
from urllib.parse import urlparse, unquote
import unicodedata
from pydantic import BaseModel

import app.config.settings as settings
from app.services.lodgerin import LodgerinAPI, LodgerinInternal

from app.models.schemas import (
    LocationMaps
)
import os
from enum import Enum
from typing import Union
from app.models.schemas import (
    DatePayloadItem,
    Property,
    RentalUnits
)


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


def get_all_images(all_url_images: list) -> list:

    if not all_url_images:
        return []

    all_images = all_url_images.split(",")
    all_images = list(map(lambda url: re.sub(r"\\/", "/", url), all_images))
    all_images = get_all_imagenes(all_images)
    return all_images


def clean_information_html(text):
    """
    This function receives a text with HTML tags and returns the cleaned text.

    :param text: str - Text with HTML tags.
    :return: str - Cleaned text without HTML tags.
    """
    cleaned = re.sub(r"<.*?>", "", text)
    cleaned = re.sub(
        r"\s+", " ", cleaned
    )
    return cleaned.strip()

def search_location(query) -> LocationMaps:
    lodgerin_api = LodgerinInternal()
    address = lodgerin_api.search_location(query)
    if address:
        location = LocationMaps(
            boundingbox=address['boundingbox'],
            lat=address['lat'],
            lon=address['lon'],
            address=address['address'],
            fullAddress=address['fullAddress'],
            number=address['number'],
            country=address['country'],
            countryCode=address['countryCode'],
            state=address['state'],
            city=address['city'],
            street=address['street'],
            postalCode=address['postalCode'],
            prefixPhone=address['prefixPhone'],
        )
        return location
    else:
        location = LocationMaps(
            boundingbox="",
            lat="",
            lon="",
            address="",
            fullAddress="",
            number="",
            country="",
            countryCode="",
            state="",
            city="",
            street="",
            postalCode="",
            prefixPhone="",
        )
        return location

def initialize_scraping_context(email: str):
    try:
        lodgerin_api = LodgerinInternal(email)
        api_key = lodgerin_api.get_api_key(email)
        api_client = LodgerinAPI(api_key)
        api_client.load_all_data()
        mapped_data = api_client.get_mapped_data()
        mapped_data["api_key"] = {"data": [{"id": email, "name": api_key}]}
        return mapped_data
    except Exception as e:
        print(f"Error durante la inicialización del contexto de scraping: {str(e)}")
        raise

def initialize_scraping_context_maps(email_map):
    """
    Inicializa el contexto de scraping para un mapeo de identificadores y correos electrónicos.

    :param email_map: Un diccionario donde las claves son identificadores (por ejemplo, ubicaciones)
                      y los valores son correos electrónicos.
    :return: Un diccionario con los datos mapeados.
    """
    try:
        if not isinstance(email_map, dict) or not all(isinstance(k, str) and isinstance(v, str) for k, v in email_map.items()):
            raise ValueError("El parámetro email_map debe ser un diccionario con claves y valores de tipo string.")

        combined_mapped_data = {"api_key": {"data": []}}

        for location, email in email_map.items():
            lodgerin_api = LodgerinInternal(email)
            api_key = lodgerin_api.get_api_key(email)
            api_client = LodgerinAPI(api_key)
            api_client.load_all_data()
            mapped_data = api_client.get_mapped_data()
            
            combined_mapped_data["api_key"]["data"].append({
                "id": email,
                "location": location,
                "name": api_key,
            })

        return combined_mapped_data
    except Exception as e:
        print(f"Error durante la inicialización del contexto de scraping: {str(e)}")
        raise


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

def extract_id_name(data):
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

def search_feature_with_map(items_features, elements_features, equivalences):
    true_ids = set()

    for item_feature in items_features:
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
                true_ids.add(element_id)

    return list(true_ids)

def decode_clean_string(url):
    """
    Extrae y limpia el reference_code desde una URL.
    - Decodifica caracteres URL.
    - Elimina acentos del texto.

    Args:
        url (str): La URL de la cual extraer el reference_code.

    Returns:
        str: El reference_code limpio.
    """
    parsed_url = urlparse(url)
    reference_code = parsed_url.path.split("/")[-1]

    decoded_reference_code = unquote(reference_code)

    normalized_reference_code = unicodedata.normalize('NFKD', decoded_reference_code)
    reference_code_without_accents = ''.join(
        char for char in normalized_reference_code if not unicodedata.combining(char)
    )
    
    return reference_code_without_accents


def extract_area(description):
    """
    Extrae el área en metros cuadrados de un texto si está presente.

    Args:
        description (str): El texto del que se desea extraer el área.

    Returns:
        float or None: El área en m2 si se encuentra, o None si no está presente.
    """
    match = re.search(r"\b(\d+(?:\.\d+)?)\s*m2\b", description, re.IGNORECASE)
    if match:
        return float(match.group(1))
    return None

def extract_cost(cost_text):
    """
    Extrae el costo en euros de un texto si está presente.

    Args:
        cost_text (str): El texto del que se desea extraer el costo.

    Returns:
        float or None: El costo en euros si se encuentra, o None si no está presente.
    """
    match = re.search(r"€\s*([\d,]+\.\d+)", cost_text)
    if match:
        return float(match.group(1).replace(",", ""))
    return None

def read_json() -> dict:
    """
    Lee un archivo JSON y lo convierte en un diccionario de Python.
    """
    try:
        with open(settings.ELEMENTS_JSON, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: El archivo {settings.ELEMENTS_JSON} no se encontró.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: El archivo {settings.ELEMENTS_JSON} no es un JSON válido.")
        return {}
    except Exception as e:
        print(f"Error inesperado: {e}")
        return {}

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
        raise ValueError(
            "item must be an instance of RentalUnits or Property or Calendar."
        )

    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)

    with open(json_file_path, "a", encoding="utf-8-sig") as json_file:
        json.dump(item.dict(), json_file, indent=4)

    print(f"Datos guardados en: {json_file_path}")
