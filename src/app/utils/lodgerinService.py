import requests
from app.utils.constants import LODGERIN_API
from typing import Optional, List,Dict


class LodgerinAPI:
    def __init__(self, api_key, lang="en"):
        self.base_url = LODGERIN_API
        self.headers = {"x-access-apikey": api_key, "x-access-lang": lang}

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

    def get_features(self):
        url = f"{self.base_url}/elements/features"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred: {err}")
        except Exception as err:
            print(f"An error occurred: {err}")
        return None

    def get_property_types(self):
        url = f"{self.base_url}/elements/properties-types"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred: {err}")
        except Exception as err:
            print(f"An error occurred: {err}")
        return None

    def get_elements(self):
        url = f"{self.base_url}/elements/contract-types"
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
            error_message = response.json() if response.content else "No additional error details provided"
            print(f"HTTP error occurred: {http_err} - Response content: {error_message}")
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
            error_message = response.json() if response.content else "No additional error details provided"
            print(f"HTTP error occurred: {http_err} - Response content: {error_message}")
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

