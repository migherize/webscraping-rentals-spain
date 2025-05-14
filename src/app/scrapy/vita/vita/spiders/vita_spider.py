import json
import scrapy
import requests
from os import path
from pathlib import Path

from app.scrapy.vita.vita import items
from scrapy.selector.unified import Selector

from app.scrapy.vita.vita.enum_vita import (
    ConfigXpath,
    ConfigPropertyRequests,
    ConfigAllRentalUnitsRequests,
    ConfigRentalUnitRequests,
)
from app.models.enums import Pages

class VitaSpiderSpider(scrapy.Spider):
    name = "vita_spider"
    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "AUTOTHROTTLE_ENABLED": True,
        "LOG_LEVEL": "INFO",
    }

    def __init__(self, context=None, *args, **kwargs):

        super(VitaSpiderSpider, self).__init__(*args, **kwargs)
        item_input_output_archive: dict[str, str] = {
            "output_folder_path": "./",
            "output_folder_name": f"{Pages.vita.value}",
            "file_name": "vitastudent.json",
            "processed_name": "vitastudent_refined.json",
            "refine": kwargs.pop("refine", "0"),
        }

        self.items_spider_output_document = {
            key_data: kwargs.pop(key_data, item_input_output_archive[key_data])
            for key_data in item_input_output_archive.keys()
        }
        self.items_spider_output_document["output_folder"] = path.join(
            self.items_spider_output_document["output_folder_path"],
            self.items_spider_output_document["output_folder_name"],
        )

        Path(self.items_spider_output_document["output_folder"]).mkdir(
            parents=True, exist_ok=True
        )
        self.context = json.loads(context) if isinstance(context, str) else {}

    def start_requests(self):
        """
        Inicio de la pagina principal
        """
        if self.items_spider_output_document['refine'] == '1':
            self.logger.info("Proceso de refinado para: %s", self.name)
            return []

        BASE_URL = "https://www.vitastudent.com/en/ciudades/"
        CITIES = ["barcelona", "leeds", "liverpool", "london", "manchester"]

        for city in CITIES:
            yield scrapy.Request(url=f"{BASE_URL}{city}/", callback=self.parse, dont_filter=True)

    def parse(self, response: Selector):

        urls_property = response.xpath(ConfigXpath.ALL_URL_PROPERTY.value)
        if not urls_property:
            self.logger.info('Sin URL de propiedades para: [%s]', response.url)
            return None

        for url_property in urls_property.getall():
            yield scrapy.Request(url_property, callback=self.parse_property, dont_filter=True)

    def parse_property(self, response: Selector):

        data_property: dict[str, str] = {}
        data_property['property_city'] = response.url.split('/')[-3]
        data_property['property_url'] = response.url
        data_property |= get_data_general(response, ConfigXpath.BASIC_DATA_PROPERTY.value)

        data_property['property_description_es'] = get_description_es(
            response.url, ConfigXpath.BASIC_DATA_PROPERTY.value['property_description_en']
        )

        # ------------------------------------------------------------------------------------------
        # obtener el Costo
        developmentid = response.xpath("//div[contains(@class, '__price')]/div/@data-developmentid").get()
        data_property['property_cost'] = get_cost(developmentid)

        # ------------------------------------------------------------------------------------------

        all_type_rental_units = response.xpath(ConfigXpath.TYPE_RENTAL_UNITS.value)

        if not all_type_rental_units:
            self.logger.info('No se encontraron tipos de rental units para: [%s]', response.url)
            return None

        # ------------------------------------------------------------------------------------------
        # obtener los rental units

        data_property['all_rental_units'] = []

        for type_rental_unit in all_type_rental_units.getall():
            data_rental_unit: list[dict] = get_rental_unit_information(developmentid, type_rental_unit)
            for rental_unit in data_rental_unit:
                room_code = rental_unit['link'].split("?")[0].replace("view-room-", '')
                data_property['all_rental_units'].append({
                    'rental_unit_room_code': room_code,
                    'rental_unit_url': path.join(response.url, rental_unit['link']),
                    'rental_unit_cost': rental_unit['range'],
                    'rental_unit_type': type_rental_unit,
                    'rental_unit_room_data': get_room_data_rental_unit(room_code),
                    'rental_unit_booking_data': get_booking_data_rental_unit(room_code),
                })

        item_output = items.VitaItem()
        item_output['items_output'] = data_property
        yield item_output


def get_data_general(response: Selector, items_xpath: dict[str, str]) -> dict[str, str]:
    return {
        key: list(map(clean_data, response.xpath(value).getall()))
        for key, value in items_xpath.items()
    }
    
    
def clean_data(data: str) -> str:
    char_map = {ord(c): ' ' for c in '\r\n\t\xa0,;'}
    aux_data = str(data).strip().translate(char_map)
    return aux_data.strip()


def get_data_with_requests(url: str, payload, aux_headers) -> str:
    response = requests.get(url, headers=aux_headers, params=payload)
    return response if response.status_code == 200 else []


def get_cost(developmentid: str) -> str:
    payload = ConfigPropertyRequests.PROPERTY_PAYLOAD.value.copy()
    payload['development'] = developmentid
    response = get_data_with_requests(
        url=ConfigPropertyRequests.PROPERTY_URL.value,
        payload=payload,
        aux_headers=ConfigPropertyRequests.PROPERTY_HEADERS.value
    )
    if response == []:
        return None
    return response.text
    



def get_rental_unit_information(developmentid: str, type_rental_unit: str) -> dict:
    payload = ConfigAllRentalUnitsRequests.ALL_RENTAL_UNITS_PAYLOAD.value.copy()
    payload |= {'development': developmentid, 'type': type_rental_unit}
    return get_data_with_requests(
        url=ConfigAllRentalUnitsRequests.ALL_RENTAL_UNITS_URL.value,
        payload=payload,
        aux_headers=ConfigAllRentalUnitsRequests.ALL_RENTAL_UNITS_HEADERS.value
    ).json()


def get_room_data_rental_unit(room_code: str) -> dict:
    payload = ConfigRentalUnitRequests.RENTAL_UNIT_PAYLOAD.value.copy()
    payload['code'] = room_code
    headers = ConfigRentalUnitRequests.RENTAL_UNIT_HEADERS.value.copy()
    headers['Referer'] = f"https://www.vitastudent.com/en/cities/barcelona/poblenou/view-room-{room_code}/?academicYear=2025 / 26"
    response = get_data_with_requests(
        url=ConfigRentalUnitRequests.RENTAL_UNIT_URL.value,
        payload=payload,
        aux_headers=headers,
    )
    return {} if not response else response.json()


def get_booking_data_rental_unit(room_code: str) -> dict:
    payload = ConfigRentalUnitRequests.PLUS_DATA_RENTAL_UNIT_PAYLOAD.value.copy()
    payload['code'] = room_code
    headers = ConfigRentalUnitRequests.PLUS_DATA_RENTAL_UNIT_HEADERS.value.copy()
    headers['Referer'] = f"https://www.vitastudent.com/en/cities/barcelona/poblenou/view-room-{room_code}/?academicYear=2025 / 26"
    response = get_data_with_requests(
        url=ConfigRentalUnitRequests.PLUS_DATA_RENTAL_UNIT_URL.value,
        payload=payload,
        aux_headers=headers,
    )
    return {} if not response else response.json()


def extract_room_details(response: Selector) -> dict:
    room_items = response.css('ul.vita-room-header__details li')
    if not room_items:
        return {}
    room_details = {}
    for item in room_items:
        label = item.css('div.vita-room-header__label::text').get().strip()
        value = item.xpath('normalize-space(.)').get().strip()
        room_details[label] = value
    return room_details


def get_description_es(url: str, xpath_description_es: str) -> str:
    
    aux_url = url.replace('/en/', '/es/')
    response_es = requests.get(aux_url)
    
    if not response_es.status_code == 200:
        return ['']
    
    response_es_scrapy = Selector(text=response_es.text)
    return response_es_scrapy.xpath(xpath_description_es).getall()