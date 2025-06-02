import re
import json
import unicodedata

from typing import Dict, Type, Any
from pydantic import BaseModel
from urllib.parse import urlparse, unquote

from app.config.settings import ElementsConfig
from app.services.lodgerin import LodgerinAPI, LodgerinInternal

from app.models.schemas import LocationMaps
import os
from enum import Enum
from app.models.enums import feature_map_rental_units
from typing import Union
from app.models.schemas import (
    RentalUnitsCalendarItem,
    Property,
    RentalUnits
)
from pathlib import Path


def save_to_json_file(data: list[dict], output_path: str) -> None:
    """Guarda datos en formato JSON en un archivo."""
    try:
        with open(output_path, "w", encoding="utf-8") as json_file:
            json.dump(data, json_file, ensure_ascii=False, indent=4)
    except (OSError, IOError) as e:
        print(f"Error al guardar el archivo JSON: {e}")


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


def get_all_images(all_url_images: str) -> list:

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
            boundingbox=[],
            lat=1.0,
            lon=1.0,
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
        lodgerin_api = LodgerinInternal()
        api_key = lodgerin_api.get_api_key(email)
        if api_key is None:
            print(f"[warning - initialize_scraping_context] -> El api_key es None para el correo: {email}")
            raise
            
        api_client = LodgerinAPI(api_key)
        mapped_data = api_client.get_elements()
        if mapped_data is None:
            print(f"[warning - initialize_scraping_context] -> El mapped_data es None")
            raise
        
        mapped_data = mapped_data.get('data', None)
        mapped_data["api_key"] = [{"id": email, "name": api_key}]
        return mapped_data
    except Exception as e:
        print(f"[warning - initialize_scraping_context] -> Error durante la inicialización del contexto de scraping: {str(e)}")
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
            raise ValueError("[warning - initialize_scraping_context_maps] -> El parámetro email_map debe ser un diccionario con claves y valores de tipo string.")

        combined_mapped_data = {"api_key": []}

        for location, email in email_map.items():
            lodgerin_api = LodgerinInternal()
            api_key = lodgerin_api.get_api_key(email)
            if api_key is None:
                print(f"[warning - initialize_scraping_context_maps] -> El api_key es None para el correo: {email}")
                continue

            api_client = LodgerinAPI(api_key)
            elements = api_client.get_elements()
            if elements is None:
                print(f"[warning - initialize_scraping_context_maps] -> El elements es None para el email: {email}")
                continue
            
            elements = elements.get('data', None)
            combined_mapped_data["api_key"].append({
                "id": email,
                "location": location,
                "name": api_key,
            })
            combined_mapped_data.update(elements)

        return combined_mapped_data
    except Exception as e:
        print(f"[warning - initialize_scraping_context_maps] -> Error durante la inicialización del contexto de scraping: {str(e)}")
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
        if not key in full_json:
            raise KeyError(f"Key '{key}' not found in the provided JSON")
        try:
            if isinstance(full_json[key], list):
                elements_dict[key] = model_class(
                    data=[
                        model_class.__annotations__["data"].__args__[0](**item)
                        for item in full_json[key]
                    ]
                )
            else:
                elements_dict[key] = model_class(**full_json[key])
        except Exception as e:
            raise ValueError(f"Error al procesar '{key}': {e}")
        
    return elements_dict

def extract_id_label(data):
    return {item.id: item.label for item in data}

def get_id_from_name(data_dict: list, name: str, key_name: str) -> int:
    """
    Busca el ID asociado a un nombre en un diccionario con estructura similar a "property_types" o "pension_types".

    Args:
        data_dict (dict): Diccionario que contiene una lista de datos bajo la llave "data".
        name (str): Nombre que se desea buscar.

    Returns:
        int: El ID asociado al nombre, si se encuentra. De lo contrario, retorna None.
    """
    for item in data_dict:
        if getattr(item, key_name) == name:
            return item.id
    return None

def search_feature_with_map(items_features, elements_features, equivalences):
    true_ids = set()

    # Normalizar claves y valores a minúsculas
    normalized_equivalences = {
        key.lower(): value.lower() if isinstance(value, str) else value
        for key, value in equivalences.items()
    }
    normalized_elements = {
        id_: name.lower() if isinstance(name, str) else name
        for id_, name in elements_features.items()
    }

    for item_feature in items_features:
        feature_key = item_feature.lower()
        if feature_key in normalized_equivalences:
            mapped_feature = normalized_equivalences[feature_key]
            if not mapped_feature:
                continue

            element_id = next(
                (id_ for id_, name in normalized_elements.items() if name == mapped_feature),
                None,
            )
            if element_id is not None:
                true_ids.add(element_id)
            else:
                print(f"[WARN] No match found for mapped feature '{mapped_feature}' from original '{item_feature}'")
        else:
            print(f"[WARN] Feature '{item_feature}' not found in equivalences")

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
    match = re.search(r"[€£]\s*([\d,]+\.\d+)", cost_text)
    if not match:
        match = re.search(r"(\d[\d.,]*)\s*€", cost_text)

    if match:
        amount_str = match.group(1).replace(".", "").replace(",", ".")
        try:
            return float(amount_str)
        except ValueError:
            return None

    return None

def read_json(path_document_json: str) -> list[dict]:
    """
    Lee un archivo JSON y lo convierte en una lista de diccionarios de Python.
    :param path_document_json: Ruta del archivo JSON.
    :return: Lista de diccionarios cargados desde el JSON o una lista vacía en caso de error.
    """
    try:
        with open(path_document_json, "r", encoding="utf-8") as file:
            if path_document_json.endswith('.json'):
                data = json.load(file)
            elif path_document_json.endswith('.txt'):
                data = json.loads(file)
            else:
                data = []
            if isinstance(data, dict):
                data = [data]
        return data
    except FileNotFoundError:
        print(f"⚠️ Error: El archivo '{path_document_json}' no se encontró.")
    except json.JSONDecodeError:
        print(f"⚠️ Error: El archivo '{path_document_json}' no es un JSON válido.")
    except Exception as e:
        print(f"⚠️ Error inesperado: {e}")
    
    return []

def create_json(item: Union[RentalUnits, Property, RentalUnitsCalendarItem], path_spider: str) -> None:
    class PathDocument(Enum):
        PROPERTY = os.path.join(path_spider ,"property.json")
        RENTAL_UNITS = os.path.join(path_spider ,"rental_units.json")
        CALENDAR = os.path.join(path_spider ,"calendar.json")

    current_dir = ElementsConfig.PATH_DATA
    if isinstance(item, RentalUnits):
        json_file_path = os.path.join(current_dir, PathDocument.RENTAL_UNITS.value)
    elif isinstance(item, Property):
        json_file_path = os.path.join(current_dir, PathDocument.PROPERTY.value)
    elif isinstance(item, RentalUnitsCalendarItem):
        json_file_path = os.path.join(current_dir, PathDocument.CALENDAR.value)
    else:
        raise ValueError(
            "item must be an instance of RentalUnits or Property or Calendar."
        )

    os.makedirs(os.path.dirname(json_file_path), exist_ok=True)

    # Leer el JSON si ya existe
    if os.path.exists(json_file_path):
        with open(json_file_path, "r", encoding="utf-8-sig") as json_file:
            try:
                data = json.load(json_file)
                if not isinstance(data, list):
                    data = []
            except json.JSONDecodeError:
                data = [] 
    else:
        data = []

    data.append(item.model_dump())
    with open(json_file_path, "w", encoding="utf-8-sig") as json_file:
        json.dump(data, json_file, indent=4, ensure_ascii=False)
    print(f"Datos guardados en: {json_file_path}")


def create_rental_unit_code_with_initials(property_referend_code: str, unit_index: int) -> str:

    """
        Si presenta guiones el property_referend_code, la salida son las iniciales
        
        parametros:
            - property_referend_code: Codigo del property con guiones
            - unit_index: Indice de los rental units recorridos en el for
        
        return: Iniciales seguido de guiones.
            Ejemplo:
            property_referend_code = malaga-Malaga-Centro-001
            unit_index = 1
            return 'M-M-C-001'
    """
    aux_referend = property_referend_code
    if not re.search(r'-', property_referend_code):
        return f"{aux_referend}-{unit_index + 1:03}"
    
    aux_referend = list(map(lambda x: x[0].upper(), aux_referend.split('-')[:-1]))
    aux_referend = "-".join(aux_referend)
    return f"{aux_referend}-{unit_index + 1:03}"

def filtrar_ids_validos(lista_ids):
    return [id_ for id_ in lista_ids if str(id_) in feature_map_rental_units]

def remove_accents(text: str) -> str:
    """Elimina los acentos de una cadena de texto."""
    return unicodedata.normalize("NFD", text).encode("ascii", "ignore").decode("utf-8")

def safe_attr(obj, attr, default=""):
    return getattr(obj, attr, default) if obj else default

def load_json(file_path: Path) -> Any:
    """
    Carga un archivo JSON y retorna su contenido.
    """
    with file_path.open('r', encoding='utf-8') as f:
        return json.load(f)