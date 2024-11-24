import requests
from app.utils.constants import LODGERIN_API, LODGERIN_INTERNAL, TOKEN_API_INTERNAL
from typing import Optional, List, Dict


class LodgerinInternal:
    def __init__(self, lang="en"):
        self.base_url = LODGERIN_INTERNAL
        self.headers = {"x-access-token": TOKEN_API_INTERNAL, "x-access-lang": lang}
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
            print(f"HTTP error occurred: {err}")
        except Exception as err:
            print(f"An error occurred: {err}")
        return None


class LodgerinAPI:
    def __init__(self, api_key, lang="en"):
        self.base_url = LODGERIN_API
        self.headers = {"x-access-apikey": api_key, "x-access-lang": lang}
        self.data = {}

    def get_properties(self, limit=100):
        url = f"{self.base_url}/properties?limit={limit}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred: {err}")
        except Exception as err:
            print(f"An error occurred: {err}")
        return None

    def get_rental_units(self, limit=100):
        url = f"{self.base_url}/rental-units?limit={limit}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred: {err}")
        except Exception as err:
            print(f"An error occurred: {err}")
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
            print(
                f"HTTP error occurred: {http_err} - Response content: {error_message}"
            )
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred: {req_err}")
        except Exception as err:
            print(f"An unexpected error occurred: {err}")

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
            print(
                f"HTTP error occurred: {http_err} - Response content: {error_message}"
            )
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred: {req_err}")
        except Exception as err:
            print(f"An unexpected error occurred: {err}")
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
            print(
                f"HTTP error occurred: {http_err} - Response content: {error_message}"
            )
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred: {req_err}")
        except Exception as err:
            print(f"An unexpected error occurred: {err}")
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
            print(
                f"HTTP error occurred: {http_err} - Response content: {error_message}"
            )
        except requests.exceptions.RequestException as req_err:
            print(f"Request error occurred: {req_err}")
        except Exception as err:
            print(f"An unexpected error occurred: {err}")

    def fetch_data(self, endpoint):
        """
        Realiza una solicitud GET al endpoint especificado y devuelve los datos JSON.

        Args:
            endpoint (str): Ruta del endpoint después de la base URL.

        Returns:
            dict | None: Datos JSON si la solicitud es exitosa, de lo contrario None.
        """
        url = f"{self.base_url}/{endpoint}"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred: {err}")
        except Exception as err:
            print(f"An error occurred: {err}")
        return None

    def get_contract_types(self):
        return self.fetch_data("elements/contract-types")

    def get_spaces_types(self):
        return self.fetch_data("elements/spaces-types")

    def get_property_types(self):
        return self.fetch_data("elements/properties-types")

    def get_rental_units_types(self):
        return self.fetch_data("elements/rental-units-types")

    def get_features(self):
        return self.fetch_data("elements/features")

    def get_furnitures(self):
        return self.fetch_data("elements/furnitures")

    def get_languages(self):
        return self.fetch_data("elements/languages")

    def get_pension_types(self):
        return self.fetch_data("elements/pension-types")

    def save_to_data(self, key, endpoint):
        """
        Guarda la información obtenida de un endpoint en el diccionario `self.data`.

        Args:
            key (str): Nombre con el que se almacenarán los datos en el diccionario.
            endpoint (str): Endpoint de la API que se utilizará para obtener los datos.
        """
        result = self.fetch_data(endpoint)
        if result is not None:
            self.data[key] = result
        else:
            print(f"No se pudo obtener datos del endpoint: {endpoint}")

    def load_all_data(self):
        """
        Carga todos los datos relevantes desde la API y los almacena en `self.data`.
        """
        self.save_to_data("contract_types", "elements/contract-types")
        self.save_to_data("spaces_types", "elements/spaces-types")
        self.save_to_data("property_types", "elements/properties-types")
        self.save_to_data("rental_units_types", "elements/rental-units-types")
        self.save_to_data("features", "elements/features")
        self.save_to_data("furnitures", "elements/furnitures")
        self.save_to_data("languages", "elements/languages")
        self.save_to_data("pension_types", "elements/pension-types")

    def get_mapped_data(self):
        """
        Devuelve todos los datos almacenados en `self.data`.

        Returns:
            dict: Diccionario con toda la información mapeada.
        """
        return self.data
