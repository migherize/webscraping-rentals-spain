# coding=utf-8
import scrapy
import requests
import app.utils.constants as constants
import app.models.enums as models

from os import path
from enum import Enum
from pathlib import Path
from scrapy.selector.unified import Selector

from app.scrapy.common import read_json

from .. import items
from ..constants_spider import item_custom_settings, item_input_output_archive

from ..utils_refine_data import *


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

    ALL_LINK_RENTAL_UNITS = "//h4[contains(@class, 'product-tile')]/../@href"

    # -----------------------------------------------------------------
    # Rental units

    ITEMS_RENTAL_UNITS = {
        "PROPERTY_AND_CITY": "//div[@class='sticky']/h4/text()",
        "NAME_RENTAL_UNIT": "//div[@class='sticky']/h3/text()",
        "COST": "//div[@class='sticky']/h6/text()",
        "TIME_RESERVETION": "//span[contains(@id, 'select2-tenancy-dropdown-container')]//@title",
        "DESCRIPTION_RENTAL_UNIT": "//div[contains(@class, 'product__description')]//p//text()",
        "ALL_INCLUSIVE": "//div[contains(@class, 'product__description')]//ul//text()",
        "ROOM_FEATURE": "//h2[contains(text(), 'Room features')]/..//article//text()",
        "SOCIAL_SPACES": "//h2[contains(text(), 'included')]/..//article//h6/text()|//h2[contains(text(), 'Social Space')]/..//article//text()",
        "STATUS": "//div[@id='cm-placement-product-details']//p[contains(text(), 'SOLD OUT')]/text()",
    }

    ITEMS_PICTURE_RENTAL_UNITS = "//picture[contains(@class, 'gallery-carousel__item--modal')]"


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

        # -----------------------------------------------------------------
        # if folder not exists create one
        Path(self.items_spider_output_document["output_folder"]).mkdir(
            parents=True, exist_ok=True
        )

        self.property_filter_city = (
            'madrid',
        )

        self.all_languages = (
            'en-us',
            'en-gb',
            'zh-cn',
            'es-es',
            'ca-es',
            'de-de',
            'it-it',
        )

        self.context = context


    def start_requests(self):
        """
        Inicio de la pagina principal
        """

        self.url_base = "https://yugo.com"
        url = "https://yugo.com/en-us/global/spain"

        return [scrapy.Request(
            url=url,
        )]

    def parse(self, response: Selector):

        # ---------------------------------------
        # Proceso de busqueda de las ciudades de Spain

        if not response.xpath(ConfigXpath.ARTICLE_DATA.value):
            self.logger.warning('No existen ciudades para: %s', response.url)
            return None
        
        for article_city in response.xpath(ConfigXpath.ARTICLE_DATA.value):
            data_city = extract_article_data(article_city, ConfigXpath.ITEMS_CITY_DATA.value)
            
            if not data_city['url_city'].split('/')[-1] in self.property_filter_city:
                continue

            data_city['url_city'] = self.url_base + data_city['url_city']

            yield scrapy.Request(
                url=data_city['url_city'],
                dont_filter=True,
                callback=self.parse_yugo_space,
                meta={"meta_data": data_city}
            )

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

        meta_data['aux_url_property'] = response.url

        meta_data['referend_code'] = get_referend_code(response.url)
        
        # ---------------------------------------
        # Proceso de busqueda de los rental units

        if not response.xpath(ConfigXpath.ALL_LINK_RENTAL_UNITS.value):
            self.logger.warning('No existen espacios o locacles (Rental Units) para: %s', response.url)

        else:
            urls_rental_units = response.xpath(ConfigXpath.ALL_LINK_RENTAL_UNITS.value).getall()
            meta_data['all_rental_units'] = self.get_data_rental_units(urls_rental_units)
        
        item_output = items.YugoItem()
        item_output['items_output'] = meta_data
        
        yield item_output

    def get_data_languages(self, url: str):

        all_data_languages = []

        aux_url = url.split('/spain/')[-1]

        for index_language, language in enumerate(self.all_languages):

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

    def refine_data_property(self, items_output: dict) -> dict:
        
        items = items_output.copy()

        items_refine: dict[str, function] = {
            "url_city": clean_default_only_data,
            "description_city": clean_default_only_data,
            "yugo_space_name": clean_default_only_data,
            "description_yugo_space": clean_default_only_data,
            "url_yugo_space": clean_default_only_data,
            "student_rooms": clean_default_only_data,
            "latitud": clean_default_only_data,
            "longitud": clean_default_only_data,

            "city_name": clean_default_only_data_list,
            "property_name": clean_default_only_data_list,
            
            "address_contact_and_email": clean_address_contact_and_email,
            "residence_description": clean_residence_description,
            "all_feature": clean_all_feature,
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

    def get_data_rental_units(self, urls_rental_units: list[str]):

        all_data_rental_units = []

        for partial_url_rental_unit in urls_rental_units:
            url_rental_unit = self.url_base + partial_url_rental_unit

            response_with_requests = requests.get(url_rental_unit)

            if not response_with_requests.status_code == 200:
                continue

            new_scrapy_selector = Selector(text=response_with_requests.text)
            
            items_rental_units = extractor_all_data(new_scrapy_selector, ConfigXpath.ITEMS_RENTAL_UNITS.value)
            items_rental_units['picture'] = extract_image_urls(new_scrapy_selector, ConfigXpath.ITEMS_PICTURE_RENTAL_UNITS.value)
            items_rental_units['url_rental_unit'] = url_rental_unit
            all_data_rental_units.append(items_rental_units)

        return all_data_rental_units
