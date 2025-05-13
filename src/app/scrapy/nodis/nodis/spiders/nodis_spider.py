import json
from pprint import pprint
import re
import scrapy
import requests
from os import path
from pathlib import Path
from typing import Optional
from scrapy import Selector
from app.scrapy.nodis.nodis.items import NodisItem
from app.scrapy.nodis.nodis.config_enum import (
    CityNameImages,
    ConfigPages, 
    ConfigXpathProperty 
)


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
            "output_folder_name": "nodis",
            "file_name": "nodies.json",
            "processed_name": "nodies_refined.json",
            "refine": '0',
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
        self.context = json.loads(context) if context else {}

    def start_requests(self):
        if self.items_spider_output_document['refine'] == '1':
            self.logger.info("Proceso de refinado para: %s", self.name)
            return []
        return [scrapy.Request(ConfigPages.BASE_URL.value, headers=ConfigPages.HEADERS.value)]

    def parse(self, response: Selector):
        urls_property = response.xpath(ConfigPages.URL_PROPERTY.value)
        if not urls_property:
            self.logger.warning('No existen propiedades en: %s', response.url)
            return None

        for index, url_property in enumerate(urls_property.getall()):
            
            if any([
                url_property in ('', 'https://nodis.es/'), 
                re.search(r'/contact|\.greenlts\.', url_property),
            ]):
                # No aplican
                continue

            if not re.search(r'residencia', url_property):
                self.logger.warning('Chequear. Existe url de Property nueva: %s', response.url)
                continue
            
            output = self.parse_main_property_and_rental(url_property)
            if output is None:
                self.logger.warning('La url: %s fallo en la busqueda', url_property)
                continue
            
            parse_item = NodisItem()
            parse_item['items_output'] = output
            yield parse_item
            # break
    
    def parse_main_property_and_rental(self, url_property: str):
        response_property = requests.get(url_property)
        if response_property.status_code != 200:
            return None
        response = Selector(text=response_property.text)
        property: dict = self.parse_data_property(response)
        output = {
            'url_property': url_property,
            'property': property,
            'rental': []
        }
        aux_url_rental_units = property.get('URL_RENTAL_UNIT', None)
        if aux_url_rental_units is None or re.search(r'contacto', aux_url_rental_units):
            # No presenta rental units
            return output
        
        if re.search(r'stephouse', aux_url_rental_units) and re.search('malaga', aux_url_rental_units):
            # El caso es para Malaga
            # Caso Particular. Tomado por Default la fuente del rental
            aux_url_rental_units = "https://stephousemalagaparmenides.greenlts.es/"
            property['URL_RENTAL_UNIT'] = aux_url_rental_units
            pass

        elif not re.search(r'greenlts', aux_url_rental_units):
            self.logger.info(
                "Formato diferente a 'greenlts'. URL de la propiedad: %s URL de los rental units: %s. Chequearlo!", 
                url_property, 
                aux_url_rental_units
            )
            return output

        data_hotel_and_rental_units = self.parse_rental_api_data(aux_url_rental_units)
        if data_hotel_and_rental_units is None:
            return output

        output['property']['info_hotel_property'] = data_hotel_and_rental_units['info_hotel_property']
        output['rental'] = data_hotel_and_rental_units['output_rental_units']
        return output

    def parse_data_property(self, response: Selector) -> dict:
        items_property = {
            'property_phone': response.xpath(ConfigXpathProperty.PHONE.value).re(r'\d{3}\s*\d{2}\s*\d{2}\s*\d{2}'),
            'property_name': response.xpath(ConfigXpathProperty.NAME.value).get(),
            'property_images': response.xpath(ConfigXpathProperty.IMAGES.value).getall(),
            'property_video': response.xpath(ConfigXpathProperty.VIDEO.value).get(),
            'property_features': response.xpath(ConfigXpathProperty.FEATURES.value).getall(),
            'property_description_es': {
                'property_description_1_es': response.xpath(ConfigXpathProperty.DESCRIPTION_1.value).getall(),
                'property_description_2_es': response.xpath(ConfigXpathProperty.DESCRIPTION_2.value).getall(),
            },
            'property_description_en': {
                'property_description_1_en': response.xpath(ConfigXpathProperty.DESCRIPTION_1.value).getall(),
                'property_description_2_en': response.xpath(ConfigXpathProperty.DESCRIPTION_2.value).getall(),
            },
            'property_aux_address': response.xpath(ConfigXpathProperty.AUX_ADDRESS_PROPERTY.value).getall()
        }

        clean_items(items_property)
        items_property['property_name'] = clean_property_name(items_property['property_name'])
        items_property['property_images'] = check_images(items_property['property_images'])

        items_property['property_description_en'] = self.parse_description_other_language(response, 'en-GB')

        # Existen casos donde solo presenta un formulario
        flag_rental_units = True if not response.xpath(ConfigPages.CONTACT.value) else False
        items_property['URL_RENTAL_UNIT'] = (
            response.xpath(ConfigXpathProperty.URL_RENTAL_UNIT.value).get()
            if flag_rental_units else None
        )
        return items_property
    
    def parse_description_other_language(self, response: Selector, language_code: str) -> dict[str, str]:

        code = {
            "en-GB": ("en-GB", "en"),
        }.get(language_code, None)

        if code is None:
            return {
                "property_description_1_en": '',
                "property_description_2_en": '',
            }

        url_property_language = response.xpath(f"//a[contains(@hreflang, '{code[0]}')]/@href").get()

        if url_property_language is None:
            return {
                "property_description_1_en": '',
                "property_description_2_en": '',
            }

        response_property_language = requests.get(url_property_language)
        if response_property_language.status_code != 200:
            return {
                f"property_description_1_{code[1]}": '',
                f"property_description_2_{code[1]}": '',
            }

        response_language = Selector(text=response_property_language.text)

        description_output = {
            f"property_description_1_{code[1]}": response_language.xpath(ConfigXpathProperty.DESCRIPTION_1.value).getall(),
            f"property_description_2_{code[1]}": response_language.xpath(ConfigXpathProperty.DESCRIPTION_2.value).getall(),
        }

        return description_output


    def parse_rental_api_data(self, url_base: str) -> Optional[dict]:
        url_base = url_base.replace('/lang/en', '')
        url_api = url_base + "/api"
        url_data = url_base + "/api/app/data"

        api_info = requests.get(url_api)
        data_info = requests.get(url_data)
        
        if all([api_info.status_code != 200, data_info.status_code != 200]):
            self.logger.warning('Problemas para obtener los rental units de:  %s', url_base)
            return None
        
        try:
            api_info: dict = api_info.json()
            data_info: dict = data_info.json()
        except Exception as error:
            self.logger.warning('Problemas para obtener los rental units de:  %s', [url_api, url_data])
            return None

        info_hotel_property = data_info.get('data', {}).get('data', {}).get("hotel", {})
        all_rental_units = data_info.get('data', {}).get('data', {}).get("masters", {}).get("roomTypes", [])
        
        if all_rental_units == []:
            return {
                "info_hotel_property": info_hotel_property, 
                "output_rental_units" : []
            }

        output_rental_units = self.extractor_info_rental_unit(all_rental_units)

        # TODO: Buscar en api_info si existe data relevante de los rental_units (Pendiente si es necesario)

        return {
                "info_hotel_property": info_hotel_property, 
                "output_rental_units" : output_rental_units
            }

    def extractor_info_rental_unit(self, all_rental_units: list[dict]) -> dict[str, str]:
        output = []
        for rental_unit in all_rental_units:
            data = {
                "rental_name": rental_unit['name'],
                "rental_id": rental_unit['id'],
                "rental_description": rental_unit['description'],
                "rental_images": {
                    "rental_image_name": rental_unit['image']['name'],
                    "rental_image_thumbUrl": rental_unit['image']['thumbUrl'],
                    "rental_image_url": rental_unit['image']['url'],
                },
            }
            data['rental_description'] = clean_data(extract_text_html(data['rental_description']))
            output.append(data)
        return output


def extract_text_html(text_html: str) -> Optional[str]:
    selector = Selector(text=text_html)
    clean_text = ' '.join(selector.xpath('//text()').getall()).strip()
    return clean_text or None


def clean_data(data: str) -> str:
    data = re.sub(r'\n|\t|\r|\xa0|\s{2,}', ' ', data).strip()
    return data


def clean_items(data: dict):
    for key, value in data.items():
        if isinstance(value, list):
            data[key] = list(map(clean_data, value))
            data[key] = list(filter(None, data[key]))
        elif isinstance(value, str):
            data[key] = clean_data(data[key])
        elif isinstance(value, dict):
            print('La data es un diccionario:', key)
        


def clean_property_name(property_name: str) -> tuple[str, str]:
    property_name = property_name.split('-')[0].replace('Nodis', '').strip()
    return property_name


def check_images(images: list[str]) -> list[str]:
    aux_images = remove_duplicate_images(images.copy())
    flag = None
    position = 3

    search_images: dict[str, str] = CityNameImages.SEARCH_IMAGES.value

    for key, value in search_images.items():
        if re.search(value, aux_images[position]):
            flag = key
            break

    if flag is None:
        return 

    output_images = []
    for image in aux_images:
        if re.search(search_images[flag], image):
            output_images.append(image)
    return output_images


def remove_duplicate_images(image_list: list[str]) -> list[str]:
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

