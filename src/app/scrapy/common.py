import re
import json
import requests
from app.utils.lodgerinService import LodgerinAPI, LodgerinInternal
import app.utils.constants as constants

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
    
    all_images = all_url_images.split(',')
    all_images = list(map(lambda url: re.sub(r'\\/', '/', url), all_images))
    all_images = get_all_imagenes(all_images)
    return all_images

def clean_information_html(text):
    """
    This function receives a text with HTML tags and returns the cleaned text.
    
    :param text: str - Text with HTML tags.
    :return: str - Cleaned text without HTML tags.
    """
    # Remove HTML tags
    cleaned = re.sub(r'<.*?>', '', text)  # Remove any HTML tags
    cleaned = re.sub(r'\s+', ' ', cleaned)  # Replace multiple spaces with a single space
    return cleaned.strip()  # Remove leading and trailing whitespace

def initialize_scraping_context(email: str):
    try:
        lodgerin_api = LodgerinInternal(email)
        api_key = lodgerin_api.get_api_key(email)
        api_client = LodgerinAPI(api_key)
        api_client.load_all_data()
        mapped_data = api_client.get_mapped_data()
        mapped_data['api_key'] = {
            "data": [
                {
                    "id": email,
                    "name": api_key
                }
            ]
        }
        return mapped_data
    except Exception as e:
        print(f"Error durante la inicialización del contexto de scraping: {str(e)}")
        raise


def read_json() -> dict:
    """
    Lee un archivo JSON y lo convierte en un diccionario de Python.
    """
    try:
        with open(constants.ELEMENTS_JSON, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data
    except FileNotFoundError:
        print(f"Error: El archivo {constants.ELEMENTS_JSON} no se encontró.")
        return {}
    except json.JSONDecodeError:
        print(f"Error: El archivo {constants.ELEMENTS_JSON} no es un JSON válido.")
        return {}
    except Exception as e:
        print(f"Error inesperado: {e}")
        return {}