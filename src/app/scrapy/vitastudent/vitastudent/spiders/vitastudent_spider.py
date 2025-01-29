import scrapy
import requests

from .. import items
from scrapy.selector.unified import Selector

from enum import Enum
from os import path
from pathlib import Path


class ConfigXpath(Enum):
    ALL_URL_PROPERTY = "//a[contains(@class, 'view-building')]/@href"
    BASIC_DATA_PROPERTY = {
        'property_name': "//h1/text()",
        'property_address': "//div[contains(@class, 'address')]/text()",
        'property_description': "//div[contains(@class, '__excerpt')]//text()",
        'property_feature': "//div[contains(@class, 'features__row')]//li//text()",
        'property_plans': "//a[contains(@href, '.pdf')]/@href",
        'property_images': "(//div[contains(@class, 'glide__slides')])[1]//img/@src",
        'property_tours_360': "//a[contains(@href, '/show/')]/@href"
    }
    TYPE_RENTAL_UNITS = "//div[@class='room-types-app']/@data-type"
    ALL_URL_RENTAL_UNITS = "//div[contains(@class, 'wp-block-button')]//@href"


class ConfigPropertyRequests(Enum):
    PROPERTY_URL = 'https://www.vitastudent.com/wp-json/student-accommodation/v1/development'
    PROPERTY_PAYLOAD = {
            'availability': 'true',
            # 'development': developmentid,     # Este parametro se agrega en la funcion
            "year": "2025 / 26",
            "lang": "es",
            "_locale": "user"            
        }
    PROPERTY_HEADERS = {
            "accept": "application/json, */*;q=0.1",
            "accept-language": "es-419,es;q=0.9,en-US;q=0.8,en;q=0.7",
            "cookie": "cookieyes-consent=consentid:NUVJdUNZSXNxeFlQTEwxRWlwUTgzd3dvZWZmZTJnaXg,consent:yes,action:yes,necessary:yes,functional:yes,analytics:yes,performance:yes,advertisement:yes,other:yes; _gcl_au=1.1.1681232971.1737074892; _ga=GA1.1.1091692651.1737074864; _scid=PFDWHVi8cpixtdt5jV5u9zplkpnWpVhL; _tt_enable_cookie=1; _ttp=UFWnD6hnU8__EvgFuosO3OpDrPL.tt.1; _fbp=fb.1.1737074906085.394986535714041988; pll_language=es; _ScCbts=[]; _sctr=1|1737864000000; _uetsid=12ca5510dc3b11ef9434793d09db0ced|v4vu0|2|fsx|0|1852; _scid_r=T9DWHVi8cpixtdt5jV5u9zplkpnWpVhLSEZ7Tw; _uetvid=a89305b0d46c11efb8a7098fb78301a3|4l5uns|1737943876155|5|1|bat.bing.com/p/insights/c/u; _ga_RSV8LEC89Z=GS1.1.1737933175.3.1.1737944130.60.0.1499288122",
            "priority": "u=1, i",
            "referer": "https://www.vitastudent.com/es/ciudades/barcelona/poblenou/",
            "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36"
        }


class ConfigAllRentalUnitsRequests(Enum):
    ALL_RENTAL_UNITS_URL = 'https://www.vitastudent.com/wp-json/student-accommodation/v1/rooms'
    ALL_RENTAL_UNITS_PAYLOAD = {
        # "development": developmentid,     # Este parametro se agrega en la funcion
        # "type": type_rental_unit,         # Este parametro se agrega en la funcion
        "year": "2025 / 26",
        "availability": "true",
        "lang": "en",
        "_locale": "user"
    }
    ALL_RENTAL_UNITS_HEADERS = {
        "sec-ch-ua-platform": "\"Windows\"",
        "Referer": "https://www.vitastudent.com/en/cities/barcelona/poblenou/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
        "Accept": "application/json, */*;q=0.1",
        "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0"
    }
    
    
class ConfigRentalUnitRequests(Enum):
    RENTAL_UNIT_URL = "https://www.vitastudent.com/wp-json/student-accommodation/v1/room"
    RENTAL_UNIT_PAYLOAD = {
            # "code": room_code,        # Este parametro se agrega en la funcion
            "year": "2025 / 26",
            "availability": "false",
            "lang": "en",
            "_locale": "user"
        }
    RENTAL_UNIT_HEADERS = {
            "sec-ch-ua-platform": "\"Windows\"",
            # "Referer": f"https://www.vitastudent.com/en/cities/barcelona/poblenou/view-room-{room_code}/?academicYear=2025 / 26",     # Este parametro se agrega en la funcion
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "application/json, */*;q=0.1",
            "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0"
        }

    PLUS_DATA_RENTAL_UNIT_URL = "https://www.vitastudent.com/wp-json/student-accommodation/v1/booking"
    PLUS_DATA_RENTAL_UNIT_PAYLOAD = {
            # "code": room_code,        # Este parametro se agrega en la funcion
            "year": "2025 / 26",
            "lang": "en",
            "_locale": "user"
        }
    PLUS_DATA_RENTAL_UNIT_HEADERS = {
            "sec-ch-ua-platform": "\"Windows\"",
            # "Referer": f"https://www.vitastudent.com/en/cities/barcelona/poblenou/view-room-{room_code}/?academicYear=2025 / 26",     # Este parametro se agrega en la funcion
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
            "Accept": "application/json, */*;q=0.1",
            "sec-ch-ua": "\"Google Chrome\";v=\"131\", \"Chromium\";v=\"131\", \"Not_A Brand\";v=\"24\"",
            "sec-ch-ua-mobile": "?0"
        }


class VitastudentSpiderSpider(scrapy.Spider):
    name = "vitastudent_spider"
    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "AUTOTHROTTLE_ENABLED": True,
        "LOG_LEVEL": "INFO",
        # "LOG_FORMAT": '%(asctime)s [%(levelname)s] %(message)s',
        # "LOG_DATEFORMAT": '%Y-%m-%d %H:%M:%S',
        # "LOGFILE": 'vita_student.log'
    }
    start_urls = [
        "https://www.vitastudent.com/en/ciudades/barcelona/",
    ]

    def __init__(self, context=None, *args, **kwargs):

        super(VitastudentSpiderSpider, self).__init__(*args, **kwargs)

        item_input_output_archive: dict[str, str] = {
            "output_folder_path": "./",
            "output_folder_name": "data",
            "file_name": "vitastudent.json",
            "processed_name": "vitastudent_refined.json",
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

        item_output = items.VitastudentItem()
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
    return get_data_with_requests(
        url=ConfigPropertyRequests.PROPERTY_URL.value,
        payload=payload,
        aux_headers=ConfigPropertyRequests.PROPERTY_HEADERS.value
    ).text


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
