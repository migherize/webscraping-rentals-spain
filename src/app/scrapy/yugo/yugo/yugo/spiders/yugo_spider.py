# coding=utf-8
import re
import json
import scrapy
import app.utils.constants as constants
import app.models.enums as models

from pprint import pprint
from os import path
from enum import Enum
from pathlib import Path
from ast import literal_eval
from scrapy.utils.response import open_in_browser
from scrapy.selector.unified import Selector

from app.scrapy.common import read_json

from .. import items
from ..constants_spider import item_custom_settings, item_input_output_archive

from ..utils_refine_data import *

# scrapy crawl yugo_spider -a refine=0
# scrapy crawl yugo_spider -a refine=1


class ConfigXpath(Enum):
    ARTICLE_DATA = "//article[contains(a/@href, '/spain/')]"

    ITEMS_CITY_DATA = {
        'city_name': './/h4//text()',
        'description_city': './/p//text()',
        'url_city': './/a//@href',
    }

    ITEMS_YUGO_SPACE_DATA = {
        'yugo_space_name': './/h4//text()',
        'description_yugo_space': './/p//text()',
        'url_yugo_space': './/a//@href',
    }

    ITEMS_PROPERTY = {
        "city_name": "//h5[@class='residence__city']/text()",
        "property_name": "//h1[@class='residence__title']/text()",
        "address_contact_and_email": "//div[@class='residence__contact-details']//p//text()|//div[@class='address-desc']//p//text()",
        "residence_description": "//div[@class='residence__description']/p//text()",
        "student_rooms": "//a[contains(text(), 'View all rooms')]/@href",
        "all_images": "//img[contains(@src, '1.web')]/@src"
    }

    ITEMS_FEATURE = {
        'all_feature': "//article[contains(@class, 'icon-logo')]/h6/text()|//div[@class='amenities-desc']/text()"
    }



class YugoSpiderSpider(scrapy.Spider):
    name = "yugo_spider"
    custom_settings = item_custom_settings

    def __init__(self, context=None, *args, **kwargs):

        super(YugoSpiderSpider, self).__init__(*args, **kwargs)

        self.items_spider_output_document = {
            key_data: kwargs.pop(key_data, item_input_output_archive[key_data])
            for key_data in item_input_output_archive.keys()
        }
        self.items_spider_output_document["output_folder"] = path.join(
            self.items_spider_output_document["output_folder_path"],
            self.items_spider_output_document["output_folder_name"],
        )

        print("items_spider_output_document:", self.items_spider_output_document)
        # -----------------------------------------------------------------
        # if folder not exists create one
        Path(self.items_spider_output_document["output_folder"]).mkdir(
            parents=True, exist_ok=True
        )
        # # self.context = context
        # self.context = read_json()

    def start_requests(self):
        """
        Inicio de la pagina principal
        """

        if self.items_spider_output_document["refine"] == "1":
            self.logger.info("Proceso de Refinado")
            return None
        
        self.url_base = "https://yugo.com"
        url = "https://yugo.com/en-gb/global/spain"

        yield scrapy.Request(
            url=url,
        )

    def parse(self, response):

        # ---------------------------------------
        # Proceso de busqueda de las ciudades de Spain

        if not response.xpath(ConfigXpath.ARTICLE_DATA.value):
            self.logger.warning('No existen ciudades para: %s', response.url)
            return None

        for article_city in response.xpath(ConfigXpath.ARTICLE_DATA.value):
            data_city = extract_article_data(article_city, ConfigXpath.ITEMS_CITY_DATA.value)
            data_city['url_city'] = self.url_base + data_city['url_city']

            yield scrapy.Request(
                url=data_city['url_city'],
                dont_filter=True,
                callback=self.parse_yugo_space,
                meta={"meta_data": data_city}
            )
            # break

    def parse_yugo_space(self, response):

        # ---------------------------------------
        # Proceso de busqueda de los Property

        if not response.xpath(ConfigXpath.ARTICLE_DATA.value):
            self.logger.warning('No existen espacios (PROPERTY) para: %s', response.url)
            return None
        
        meta_data = response.meta.get("meta_data")

        for article_yugo_space in response.xpath(ConfigXpath.ARTICLE_DATA.value):
            data_yugo_space = extract_article_data(article_yugo_space, ConfigXpath.ITEMS_YUGO_SPACE_DATA.value)
            data_yugo_space['url_yugo_space'] = self.url_base + data_yugo_space['url_yugo_space']
            meta_data = meta_data | data_yugo_space
            yield scrapy.Request(
                url=data_yugo_space['url_yugo_space'],
                dont_filter=True,
                callback=self.parse_property_space,
                meta={"meta_data": meta_data}
            )

    def parse_property_space(self, response):

        # Proceso de extraccion de data correspondiente al Property 
        meta_data = response.meta.get("meta_data")

        items_property = extractor_all_data(response, ConfigXpath.ITEMS_PROPERTY.value)
        items_feature = extractor_all_data(response, ConfigXpath.ITEMS_FEATURE.value)
        items_geo = extraer_lat_long(response)

        meta_data = meta_data | items_property | items_feature | items_geo
        meta_data['student_rooms'] = f"{response.url}/rooms"

        meta_data = self.refine_data_property(meta_data)
        
        yield scrapy.Request(
            url=meta_data['student_rooms'],
            callback=self.parse_rental_units,
            meta={'meta_data': meta_data}
        )

    def parse_rental_units(self, response):

        item = items.YugoItem()

        meta_data = response.meta.get("meta_data")
        item['items_output'] = meta_data
        
        yield item

        # ---------------------------------------
        # Proceso de busqueda de los rental units

        # if not response.xpath(ConfigXpath.ARTICLE_DATA.value):
        #     self.logger.warning('No existen espacios o locacles (Rental Units) para: %s', response.url)
        #     return None

        # for partial_url_rental_unit in response.xpath(ConfigXpath.ARTICLE_DATA.value):
        #     # url_rental_unit = self.url_base + partial_url_rental_unit.get()
        #     # yield scrapy.Request(
        #     #     url=url_rental_unit,
        #     #     dont_filter=True,
        #     #     callback=self.parse_rental_units
        #     # )
        #     # break
        #     pass
        # pass

    def refine_data_property(self, items_output: dict) -> dict:
        items = items_output.copy()

        items_refine: dict[str, function] = {
            "city_name": clean_city_name,
            "description_city": clean_description_city,
            "url_city": clean_url_city,
            "yugo_space_name": clean_yugo_space_name,
            "description_yugo_space": clean_description_yugo_space,
            "url_yugo_space": clean_url_yugo_space,
            "property_name": clean_property_name,
            "address_contact_and_email": clean_address_contact_and_email,
            "residence_description": clean_residence_description,
            "student_rooms": clean_student_rooms,
            "all_feature": clean_all_feature,
            "latitud": clean_latitud,
            "longitud": clean_longitud,
            "all_images": clean_all_images,
        }

        for key, funtion_item in items_refine.items():
            if key in items.keys():
                items[key] = funtion_item(items[key])
            else:
                self.logger.warning(
                    'No se presenta el campo %s en los campos extraidos %s', 
                    key, 
                    items.keys()
                )

        return items


def extract_article_data(article: Selector, items_output: dict):
    return {
        key: article.xpath(value).get(default="").strip()
        for key, value in items_output.items()
    }

def extractor_all_data(response: Selector, items_output: dict):
    return {
        key: response.xpath(value).getall()
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

