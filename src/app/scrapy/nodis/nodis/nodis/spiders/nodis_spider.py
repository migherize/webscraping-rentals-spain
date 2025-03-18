import re
import json
import scrapy
import requests
from os import path
from enum import Enum
from pathlib import Path
from scrapy import Selector

from nodis.items import NodisItem
from scrapy.selector.unified import Selector

from pprint import pprint


class AllXpath(Enum):

    ALL_URL_PROPERTY = "(//div[contains(@class, 'container p-0')])[1]//a/@href"
    DATA_PROPERTY_ENGLISH = {
        'property_name': '//button[@id="dropdownMenuButton"]/../../../p[1]//text()|//span[@class="elementor-button-text"]/text()',
        'property_phone': '//button[@id="dropdownMenuButton"]/../../../p[2]/text()|//div[@data-id="0110ffb"]//text()',
        'property_images': "//@srcset",
        'property_info_1': "//div[contains(@class, 'marginNeg')]//h2//text()",
        'property_info_2': "(//div[@class='p-5'])[1]//text()",
        'property_video': "//video/@src",
        'property_features': "//figure//text()",
        'property_features_info': "(//div[@class='p-5'])[2]//text()",
    }
    URL_SPANISH = "//a[@lang='es-ES']/@href" 
    DATA_PROPERTY_SPANISH = {
        # 'property_name': '//button[@id="dropdownMenuButton"]/../../../p[1]//text()',
        'property_name': '//button[@id="dropdownMenuButton"]/../../../p[1]//text()|//span[@class="elementor-button-text"]/text()',
        'property_info_1': "//div[contains(@class, 'marginNeg')]//h2//text()",
        'property_info_2': "(//div[@class='p-5'])[1]//text()",
        'property_features': "//figure//text()",
        'property_features_info': "(//div[@class='p-5'])[2]//text()",
    }


class NodisSpiderSpider(scrapy.Spider):
    name = "nodis_spider"
    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "AUTOTHROTTLE_ENABLED": True,
        "LOG_LEVEL": "INFO",
    }

    def __init__(self, context=None, *args, **kwargs):

        super(NodisSpiderSpider, self).__init__(*args, **kwargs)
        item_input_output_archive: dict[str, str] = {
            "output_folder_path": "./",
            "output_folder_name": "data",
            "file_name": "nodies.json",
            "processed_name": "nodies_refined.json",
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
        # self.context = json.loads(context) if isinstance(context, str) else {}


    def start_requests(self):
        return [scrapy.Request("https://nodis.es/")]

    def parse(self, response: Selector):
        
        urls_property = response.xpath(AllXpath.ALL_URL_PROPERTY.value)
        if not urls_property:
            self.logger.warning('No existen propiedades')
            return None

        for index, url_property in enumerate(urls_property):
            yield scrapy.Request(
                url_property.get(),
                meta={'url_property': url_property.get()},
                callback=self.parse_main_property,
                dont_filter=False
            )
            if index == 2:
                break

    def parse_main_property(self, response: Selector):
        
        data_property = {
            'property_en': {},
            'property_es': {},
        }
        data_all_rental = {
            'rentals_units': [{}]
        }

        data_property['property_en'] = get_data_property(response, AllXpath.DATA_PROPERTY_ENGLISH.value)
        data_property['property_en']['property_url'] = response.url
        data_property['property_es']['property_url'] = response.xpath(AllXpath.URL_SPANISH.value).getall()
        if data_property['property_es']['property_url']:
            data_property['property_es'] = get_data_property(
                Selector(text=requests.get(data_property['property_es']['property_url'][0]).text),
                AllXpath.DATA_PROPERTY_SPANISH.value
            )
            data_property['property_es']['property_url'] = response.xpath(AllXpath.URL_SPANISH.value).get()

        items_output = NodisItem()
        items_output['items_output'] = data_property | data_all_rental
        yield items_output


def get_data_property(response: Selector, all_xpath: dict[str, str]) -> list[str]:

    data_property = {
        key: response.xpath(value).getall()
        for key, value in all_xpath.items()
    }
    clean_data_property(data_property)
    return data_property


def clean_data_property(data_property: dict[str, list]) -> None:

    for key, value in data_property.items():
        if key in ('property_images',):
            continue
        if isinstance(value, list):
            data_property[key] = list(map(lambda x: re.sub(r'\n|\t|\r|\xa0', ' ', x).strip(), value))
            data_property[key] = list(filter(None, data_property[key]))

    data_property['property_name'] = [data_property.get('property_name', [''])[0]]
    data_property['property_phone'] = get_phone_number(data_property.get('property_phone', []))
    data_property['property_features'] = data_property.get('property_features', [])
    data_property['property_images'] = remove_duplicate_images(data_property.get('property_images', []))
    
    for key in ('property_info_1', 'property_info_2', 'property_features_info'):
        data_property[key] = [" ".join(data_property.get(key, ['']))]

    return None


def get_phone_number(phone) -> list:

    if not phone:
        return []
    return [phone[-1]]


def remove_duplicate_images(image_list: list[str]):
    unique_images = set()
    cleaned_images = []

    if not image_list:
        return []

    for images in image_list:
        for url in images.split(", "):
            clean_url = re.sub(r"-\d{2,4}x\d{2,4}", "", url.split()[0])  # Eliminar tamaño
            if any([re.search(r'\.png', clean_url), clean_url in unique_images]):
                continue
            unique_images.add(clean_url)
            cleaned_images.append(clean_url)

    return cleaned_images