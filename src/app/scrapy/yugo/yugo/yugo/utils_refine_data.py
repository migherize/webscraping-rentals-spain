import re
import json
from urllib.parse import urljoin
from scrapy.selector.unified import Selector


def extract_article_data(article: Selector, items_output: dict):
    return {
        key: article.xpath(value).get(default="").strip()
        for key, value in items_output.items()
    }

def extractor_all_data(response: Selector, items_output: dict):
    return {
        key: clean_list(response.xpath(value).getall())
        for key, value in items_output.items()
    }

def extraer_lat_long(response):
    # Busca todos los bloques de script que contienen JSON-LD y tienen 'latitude' y 'longitude'
    json_ld_scripts = response.xpath("//script[contains(text(), 'latitude')]/text()").get()
    for json_ld in json_ld_scripts:
        try:
            # Carga cada JSON en un diccionario
            datos = json.loads(json_ld)
            # Verifica si es un diccionario y contiene la clave 'geo'
            if isinstance(datos, dict) and 'geo' in datos:
                latitud = datos['geo'].get('latitude', '')
                longitud = datos['geo'].get('longitude', '')
                if latitud and longitud:  # Verifica que ambos valores existan
                    return {
                        'latitud': latitud, 
                        'longitud': longitud
                    }
        except json.JSONDecodeError:
            continue  # Ignora errores de decodificación

    return {
        'latitud': '', 
        'longitud': '',
    }


def extract_image_urls(response: Selector, xpath: str):
    """
    Extrae URLs de imágenes desde un atributo src o desde un JSON en data-cm-responsive-media.
    
    Si las URLs son relativas, se convierten a absolutas utilizando la URL base del response.
    
    :param response: El objeto Scrapy Response.
    :param xpath: El XPath para seleccionar los elementos con atributo src o data-cm-responsive-media.
    :return: Una lista de URLs absolutas de las imágenes.
    """
    image_urls = []
    
    # Manejar el caso del atributo `src`
    src_values = response.xpath(f"{xpath}//@src").getall()
    image_urls.extend([urljoin(response.url, src) for src in src_values if not src.startswith("data:")])
    
    # Manejar el caso del atributo `data-cm-responsive-media`
    data_cm_values = response.xpath(f"{xpath}//@data-cm-responsive-media").getall()
    
    for data_cm in data_cm_values:
        
        try:
            # Búsqueda en el texto
            match = re.search(r'"300":"(\/resource\/image\/[^"]+)"', data_cm)

            # Extraer el resultado si hay un match
            if match:
                image_urls.append(f"https://yugo.com/{match.group(1)}")

        except Exception as error:
            continue
    
    return image_urls


def get_referend_code(url: str):
    if not url or not isinstance(url, str):
        return None
    data_url = url.split('/')
    return f"{data_url[-2]}-{data_url[-1]}" 


def clean_list(data: list) -> list:
    return list(filter(None, map(str.strip, data)))

# ------------------------------------

def clean_default_only_data(data: str) -> str:
    return data.strip()

def clean_default_only_data_list(data: str) -> str:
    if data and isinstance(data, list):
        return data[0].strip()
    return ''

def clean_address_contact_and_email(data: list[str]) -> str:
    """retorna solo la direccion"""
    if data and isinstance(data, str):
        return data
    if data and isinstance(data, list):
        address = ", ".join(data)
        address = re.sub(r'Tel:.+', '', address).strip()
        return address
    return ''

def clean_residence_description(data: list[str]) -> str:
    if data and isinstance(data, list):
        return re.sub(r' ', ' ', "".join(data)).strip()
    return ''

def clean_all_feature(data: list[str]) -> list[str]:
    if data and isinstance(data, list):
        return list(map(
            lambda x: re.sub(r'\n|\r', '', x),
            data
        ))
    return ['']

def clean_all_images(data: list[str]) -> list[str]:
    if data and isinstance(data, list):
        return data
    return ['']

def clean_data_languages(data: list) -> list:
    return data