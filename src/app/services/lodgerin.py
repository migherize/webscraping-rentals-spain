import logging
from typing import Dict, List, Optional

import requests
from app.config.settings import GlobalConfig, LodgerinConfig, TokenConfig,EmailConfig, ElementsConfig

class LodgerinInternal:
    def __init__(self, lang="en"):
        self.base_url = LodgerinConfig.INTERNAL_URL
        self.base_url_maps = LodgerinConfig.MAPS_INTERNAL_URL
        self.headers = {"x-access-token": TokenConfig.API_INTERNAL, "x-access-lang": lang}
        self.data = {}

    def get_api_key(self, email):
        url = f"{self.base_url}/integrations/inputs/api-key-scraping-by-email"
        try:
            response = requests.get(url, headers=self.headers, params={"email": email})
            response.raise_for_status()
            data = response.json()
            api_key = data.get("data", {}).get("apiKey")
            if not api_key:
                raise Exception("La clave 'apiKey' no se encuentra en la respuesta.")
            return api_key
        except requests.exceptions.HTTPError as err:
            logging.info(f"HTTP error occurred: {err}")
        except Exception as err:
            logging.info(f"An error occurred: {err}")
        return None

    def search_location(self, query):
        url = f"{self.base_url_maps}/maps/search"
        try:
            response = requests.get(
                url,
                headers=self.headers,
                params={"q": query, "size": 50, "region[]": "ES"},
            )
            response.raise_for_status()
            data = response.json()
            address = data.get("data", {})[0]
            if not address:
                raise Exception("La clave 'address' no se encuentra en la respuesta.")
            return address
        except requests.exceptions.HTTPError as err:
            logging.info(f"HTTP error occurred: {err}")
        except Exception as err:
            logging.info(f"An error occurred: {err}")
        return None


class LodgerinAPI:
    def __init__(self, api_key, lang="en"):
        self.base_url = LodgerinConfig.API_URL
        self.headers = {"x-access-apikey": api_key, "x-access-lang": lang}
        self.data = {}

    # GET
    def get_elements(self):
        """
        Realiza una solicitud GET al endpoint especificado y devuelve los datos JSON.

        Args:
            endpoint (str): Ruta del endpoint después de la base URL.

        Returns:
            dict | None: Datos JSON si la solicitud es exitosa, de lo contrario None.
        """
        url = f"{self.base_url}/elements"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            logging.info(f"HTTP error occurred: {err}")
        except Exception as err:
            logging.info(f"An error occurred: {err}")
        return None

    def get_properties(self, limit=100):
        url = f"{self.base_url}/properties?limit={limit}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            logging.info(f"HTTP error occurred: {err}")
        except Exception as err:
            logging.info(f"An error occurred: {err}")
        return None

    def get_rental_units(self, limit=100):
        url = f"{self.base_url}/rental-units?limit={limit}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            logging.info(f"HTTP error occurred: {err}")
        except Exception as err:
            logging.info(f"An error occurred: {err}")
        return None
 
    def get_rental_unit_calendar(
        self, rental_unit_id: str, end_date: Optional[str] = None
    ):
        """
        Obtiene el calendario de una unidad de renta específica.

        Args:
            property_id (str): ID de la propiedad.
            rental_unit_id (str): ID de la unidad de renta.
            start_date (str, opcional): Fecha inicial para el filtrado en formato 'YYYY-MM-DD'.
            end_date (str, opcional): Fecha final para el filtrado en formato 'YYYY-MM-DD'.

        Returns:
            dict: Respuesta JSON con la información del calendario o None en caso de error.
        """
        url = f"{self.base_url}/rental-units/{rental_unit_id}/calendar"

        try:
            response = requests.get(url, headers=self.headers, params=end_date)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            error_message = (
                response.json()
                if response.content
                else "No additional error details provided"
            )
            logging.info(
                f"HTTP error occurred: {http_err} - Response content: {error_message}"
            )
        except requests.exceptions.RequestException as req_err:
            logging.info(f"Request error occurred: {req_err}")
        except Exception as err:
            logging.info(f"An unexpected error occurred: {err}")
    
    # POST
    def create_or_update_property(self, property_data):
        url = f"{self.base_url}/properties"
        try:
            response = requests.post(url, json=property_data, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            error_message = (
                response.json()
                if response.content
                else "No additional error details provided"
            )
            logging.info(
                f"HTTP error occurred: {http_err} - Response content: {error_message}"
            )
        except requests.exceptions.RequestException as req_err:
            logging.info(f"Request error occurred: {req_err}")
        except Exception as err:
            logging.info(f"An unexpected error occurred: {err}")
        return None

    def create_or_update_rental_unit(self, rental_unit_data):
        url = f"{self.base_url}/rental-units"
        try:
            response = requests.post(url, json=rental_unit_data, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            error_message = (
                response.json()
                if response.content
                else "No additional error details provided"
            )
            logging.info(
                f"HTTP error occurred: {http_err} - Response content: {error_message}"
            )
        except requests.exceptions.RequestException as req_err:
            logging.info(f"Request error occurred: {req_err}")
        except Exception as err:
            logging.info(f"An unexpected error occurred: {err}")
        return None

    def create_rental_unit_calendar(
        self, rental_unit_id: str, dates: List[Dict[str, Optional[str]]]
    ):
        """
        Agrega fechas de no disponibilidad a una unidad de renta específica.

        Args:
            property_id (str): ID de la propiedad.
            rental_unit_id (str): ID de la unidad de renta.
            dates (List[Dict[str, Optional[str]]]): Lista de fechas de no disponibilidad.

        Returns:
            dict: Respuesta JSON con el resultado de la solicitud o None en caso de error.
        """
        url = f"{self.base_url}/rental-units/{rental_unit_id}/calendar"
        payload = {"dates": dates}

        try:
            response = requests.post(url, headers=self.headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            error_message = (
                response.json()
                if response.content
                else "No additional error details provided"
            )
            logging.info(
                f"HTTP error occurred: {http_err} - Response content: {error_message}"
            )
        except requests.exceptions.RequestException as req_err:
            logging.info(f"Request error occurred: {req_err}")
        except Exception as err:
            logging.info(f"An unexpected error occurred: {err}")
