import requests
from app.utils.constants import LODGERIN_API


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

    #TODO: save_property and save_rental_unit
    def create_or_update_property(self, property_data):
        url = f"{self.base_url}/properties"
        try:
            response = requests.post(url, json=property_data, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred: {err}")
        except Exception as err:
            print(f"An error occurred: {err}")
        return None

    def create_or_update_rental_unit(self, rental_unit_data):
        url = f"{self.base_url}/rental-units"
        try:
            response = requests.post(url, json=rental_unit_data, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as err:
            print(f"HTTP error occurred: {err}")
        except Exception as err:
            print(f"An error occurred: {err}")
        return None
