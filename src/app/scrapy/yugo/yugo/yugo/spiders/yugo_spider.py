# coding=utf-8
import re
import json
import scrapy
import requests
import app.utils.constants as constants
import app.models.enums as models

from pprint import pprint

from os import path
from enum import Enum
from pathlib import Path
from ast import literal_eval
from urllib.parse import urljoin
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
        "residence_description": "//div[@class='residence__description']//p//text()",
    }

    ITEMS_PROPERTY_GENERAL = {
        "address_contact_and_email": "//div[@class='residence__contact-details']//p//text()|//div[@class='address-desc']//p//text()",
        "student_rooms": "//a[contains(text(), 'View all rooms')]/@href",
        'tour_virtual': "//a[contains(@href, 'noupunt.com')]/@href",
    }

    ITEMS_PICTURE = "//section[contains(@class, 'media__container')]"

    ITEMS_FEATURE = {
        'all_feature': "//article[contains(@class, 'icon-logo')]/h6/text()|//div[@class='amenities-desc']/text()"
    }

    ITEMS_LANGUAGES = "//ul[@id='weglot-listbox']//@href"



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
        self.context = read_json()

    def start_requests(self):
        """
        Inicio de la pagina principal
        """

        if self.items_spider_output_document["refine"] == "1":
            self.logger.info("Proceso de Refinado")
            return None
        
        self.url_base = "https://yugo.com"
        url = "https://yugo.com/en-us/global/spain"

        yield scrapy.Request(
            url=url,
        )

    def parse(self, response: Selector):

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

    def parse_yugo_space(self, response: Selector):

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
            # break

    def parse_property_space(self, response: Selector):

        # Proceso de extraccion de data correspondiente al Property 
        # open_in_browser(response)
        meta_data = response.meta.get("meta_data")

        items_property = extractor_all_data(response, ConfigXpath.ITEMS_PROPERTY.value)
        items_property_general = extractor_all_data(response, ConfigXpath.ITEMS_PROPERTY_GENERAL.value)
        items_feature = extractor_all_data(response, ConfigXpath.ITEMS_FEATURE.value)
        items_geo = extraer_lat_long(response)

        meta_data = meta_data | items_property_general | items_feature | items_geo | items_property
        meta_data['student_rooms'] = f"{response.url}/rooms"

        meta_data['all_images'] = extract_image_urls(response, ConfigXpath.ITEMS_PICTURE.value)

        meta_data['second_items_property'] = self.get_data_languages(response.url)

        meta_data = self.refine_data_property(meta_data)
        
        yield scrapy.Request(
            url=meta_data['student_rooms'],
            callback=self.parse_rental_units,
            meta={'meta_data': meta_data}
        )

    def get_data_languages(self, url: str):

        all_data_languages = []
        languages = (
            'en-us',
            'en-gb',
            'zh-cn',
            'es-es',
            'ca-es',
            'de-de',
            'it-it',
        )

        aux_url = url.split('/spain/')[-1]
        for index_language, language in enumerate(languages):
            new_url = f"https://yugo.com/{language}/global/spain/{aux_url}"
            response_with_requests = requests.get(new_url)
            if not response_with_requests.status_code == 200:
                self.logger.warning('No se obtuvo info en el lenguaje: %s', url)
                continue

            html_content = response_with_requests.text
            new_selector_scrapy = Selector(text=html_content)
            items_property = extractor_all_data(new_selector_scrapy, ConfigXpath.ITEMS_PROPERTY.value)
            for key, value in items_property.items():
                items_property[key] = "".join(value).strip()
            items_property['language'] = language
            items_property['index_language'] = index_language
            all_data_languages.append(items_property)
        
        return all_data_languages


    def parse_rental_units(self, response: Selector):

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
            "second_items_property": clean_data_languages,
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
            # Expresión regular para extraer el valor
            pattern = r'"300":"(\/resource\/image\/[^"]+)"'

            # Búsqueda en el texto
            match = re.search(pattern, data_cm)

            # Extraer el resultado si hay un match
            if match:
                image_urls.append(f"https://yugo.com/{match.group(1)}")
        except Exception as error:
            continue
    
    return image_urls
