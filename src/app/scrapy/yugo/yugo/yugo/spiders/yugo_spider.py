# coding=utf-8
from pprint import pprint
import scrapy
import requests

from os import path
from pathlib import Path
from scrapy.selector.unified import Selector

from app.scrapy.yugo.yugo.yugo import items
from app.scrapy.yugo.yugo.yugo.utils_refine_data import *
from app.scrapy.yugo.yugo.yugo.enum_yugo import ConfigXpath
from ast import literal_eval

class YugoSpiderSpider(scrapy.Spider):
    name = "yugo_spider"
    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "AUTOTHROTTLE_ENABLED": True,
        "LOG_LEVEL": "INFO",
    }

    def __init__(self, context=None, *args, **kwargs):

        super(YugoSpiderSpider, self).__init__(*args, **kwargs)

        item_input_output_archive: dict[str, str] = {
            "output_folder_path": r"./",
            "output_folder_name": r"data",
            "file_name": f"yugo.json",
            "processed_name": "yugo_refined.json",
        }

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
            'sevilla'
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

        self.context = json.loads(context) if context else {}

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

            if not self.filter_city_yugo(data_city['url_city']):
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

        property_data = response.xpath(ConfigXpath.ARTICLE_DATA_VIEW_ROOMS.value)
        
        if not property_data:
            self.logger.warning('No existen espacios (PROPERTY) para: %s', response.url)
            return None
            
        meta_data = response.meta.get("meta_data")
    
        for article_yugo_space in property_data:
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

        address = ''
        if re.search(r'"translatedWordsList"', response.text):
            api_property = re.search(r'"translatedWordsList":\s?(\[.+\])}</script>', response.text)
            if api_property:
                # Presenta la api con la data de property
                all_data_property = api_property.group(1)
                all_data_property = literal_eval(all_data_property)
                address = self.extractor_address(all_data_property)

        items_property = extractor_all_data(response, ConfigXpath.ITEMS_PROPERTY.value)
        items_property_general = extractor_all_data(response, ConfigXpath.ITEMS_PROPERTY_GENERAL.value)
        items_property_general['address_contact_and_email'] = address.strip()
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
            item_output = items.YugoItem()
            meta_data['all_rental_units'] = []
            item_output['items_output'] = meta_data
            yield item_output

        else:
            urls_rental_units = response.xpath(ConfigXpath.ALL_LINK_RENTAL_UNITS.value).getall()
            urls_rental_units = list(map(lambda url_rental_units: self.url_base + url_rental_units, urls_rental_units))
            meta_data['urls_rental_units'] = urls_rental_units

            yield scrapy.Request(
                url=meta_data['student_rooms'],
                callback=self.get_all_rental_units,
                meta={"meta_data": meta_data},
                dont_filter=True
            )

    
    def get_all_rental_units(self, response):
        
        item_output = items.YugoItem()

        meta_data = response.meta.get("meta_data")
        meta_data['all_rental_units'] = []

        all_id_rental_units = re.findall(r'"contentId":\d+,', response.text)
        
        if not all_id_rental_units:
            self.logger.info('No existen Rental Units en la propiedad. %s', meta_data['aux_url_property'])
            item_output['items_output'] = meta_data
            yield item_output
            return None
            
        api_all_rental_units = []

        for conten_id in all_id_rental_units:
    
            aux_conten_id = re.search(r'(\d+)', conten_id).group(1)
            url = f"https://yugo.com/en-gb/tenancyOptionsByContentId/{aux_conten_id}"
            json_data: dict = requests.get(url).json()

            json_data['url'] = url
            json_data['aux_conten_id'] = aux_conten_id
            api_all_rental_units.append(json_data)

        if not api_all_rental_units:
            self.logger.info('No existen Rental Units disponibles. %s', meta_data['aux_url_property'])

        else:
            meta_data['all_rental_units'] = self.get_data_rental_units(
                meta_data['urls_rental_units'],
                api_all_rental_units
            )

        item_output = items.YugoItem()
        item_output['items_output'] = meta_data
        yield item_output


    def get_data_rental_units(self, urls_rental_units: list[str], api_all_rental_units: list[dict]):

        all_data_rental_units = []

        for api_data_rental_unit in api_all_rental_units:

            content_id = api_data_rental_unit['aux_conten_id']

            for url_rental_unit in urls_rental_units:

                if not url_rental_unit.endswith(content_id):
                    continue
                
                response_with_requests = requests.get(url_rental_unit)

                if not response_with_requests.status_code == 200:
                    continue

                new_scrapy_selector = Selector(text=response_with_requests.text)
                
                items_rental_units = extractor_all_data(new_scrapy_selector, ConfigXpath.ITEMS_RENTAL_UNITS.value)
                items_rental_units['picture'] = extract_image_urls(new_scrapy_selector, ConfigXpath.ITEMS_PICTURE_RENTAL_UNITS.value)
                items_rental_units['url_rental_unit'] = url_rental_unit
                all_data_rental_units.append({
                    'api_data_rental_unit': api_data_rental_unit,
                    'response_data_rental_units': items_rental_units,
                })

        return all_data_rental_units

    
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


    def filter_city_yugo(self, url: str) -> bool:
        """
        Filtrar solo las ciudades que se encuentran en self.property_filter_city
        """
        return True if url.split('/')[-1] in self.property_filter_city else False
    
    def extractor_address(self, data_property: list[str]) -> str:
        address = ''
        try:
            for index, data in enumerate(data_property):
                if data == 'Address':
                    address = data_property[index + 1: index + 3]
                    if address[-1].startswith(('Telf:', 'Tel:', 'tel:')):
                        address.pop()
                    address = " ".join(address)
                    break
        except Exception as error:
            self.logger.warning('Error en extraer la direccion. Error: %s', error)
        return address