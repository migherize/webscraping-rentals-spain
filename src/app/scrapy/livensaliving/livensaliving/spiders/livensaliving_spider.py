import json
import scrapy
from os import path
from pathlib import Path
from scrapy import Selector
from scrapy.http import Response
from app.scrapy.livensaliving.livensaliving.items import LivensalivingItem
from app.scrapy.livensaliving.livensaliving.config_enum import (
    ConfigPages,
    ConfigCity,
    ConfigProperty,
)


class LivensalivingSpiderSpider(scrapy.Spider):
    name = "livensaliving_spider"
    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "AUTOTHROTTLE_ENABLED": True,
        "LOG_LEVEL": "INFO",
    }

    def __init__(self, context=None, *args, **kwargs):
        super(LivensalivingSpiderSpider, self).__init__(*args, **kwargs)

        item_input_output_archive: dict[str, str] = {
            "output_folder_path": "./",
            # "output_folder_name": "livensaliving",
            "output_folder_name": "output",
            "file_name": "livensaliving.json",
            "processed_name": "livensaliving_refined.json",
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
        
        for country, url_country in ConfigPages.ITEMS_COUNTRIES.value.items():
            self.logger.info('Pais: %s', country)
            yield scrapy.Request(url_country)

    def parse(self, response: Response):

        if response.status != 200:
            self.logger.warning('Problemas de conexion para la url: %s', response.url)
            return None

        # Busqueda de ciudades

        if not response.xpath(ConfigCity.PIVOTE.value):
            self.logger.warning('No existen estados. Chequear url: %s', response.url)
            return None
        
        for response_state in response.xpath(ConfigCity.PIVOTE.value):
            info_state = {
                'state': response_state.xpath(ConfigCity.TITLE.value).get(),
                'url': response_state.xpath(ConfigCity.URL.value).get(),
                'description': response_state.xpath(ConfigCity.DESCRIPTION.value).get(),
            }
            yield scrapy.Request(
                info_state['url'],
                meta={'info_state': info_state},
                dont_filter=True,
                callback=self.parse_properties
            )
    
    def parse_properties(self, response: Response):

        if response.status != 200:
            self.logger.warning('Problemas de conexion para la url: %s', response.url)
            return None

        # Busqueda de las propiedades

        if not response.xpath(ConfigProperty.PIVOTE.value):
            self.logger.warning('No existen ciudades. Chequear url: %s', response.url)
            return None
        
        info_state = response.meta.get('info_state')
        for response_state in response.xpath(ConfigProperty.PIVOTE.value):
            info_property = {
                'name': response_state.xpath(ConfigProperty.NAME.value).getall(),
                'title': response_state.xpath(ConfigProperty.TITLE.value).getall(),
                'description': response_state.xpath(ConfigProperty.DESCRIPTION.value).getall(),
                'url': response_state.xpath(ConfigProperty.URL.value).get(),
            }
            
            output_item = LivensalivingItem()
            
            if info_property['url'] is None:
                self.logger.warning('No existe url para la propiedad: %s', info_property['name'])
                output_item['items_output'] = {
                    'info_state': info_state,
                    'info_property': info_property,
                }
                yield output_item
                continue

            info_property['url'] = "/".join(info_property['url'].split('/')[0:-2])
            output_item['items_output'] = {
                'info_state': info_state,
                'info_aux_property': info_property,
            }

            yield scrapy.Request(
                info_state['url'],
                meta={'output_item': output_item},
                headers={
                    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
                    "accept-language": "es-419,es;q=0.9,en-US;q=0.8,en;q=0.7",
                    "cache-control": "max-age=0",
                    "cookie": ("CookieConsent={stamp:'tRAqq6jQB9Pw64Lqi6DUjAf/IQdZ8421B7qf6XCkcoc0P95P259tHw==',necessary:true,"
                            "preferences:true,statistics:true,marketing:true,method:'explicit',ver:3,utc:1747001041976,region:'ve'}; "
                            "_gcl_au=1.1.290786704.1747001040; _ga=GA1.1.2106477809.1747001030; _fbp=fb.1.1747001048730.329454754146935148; "
                            "_clck=zg7mr|2|fvu|1|1957; wp-wpml_current_language=es; _ga_RD2LSE0G9J=GS2.1.s1747016231$o2$g1$t1747019908$j60$l0$h903351262"),
                    "priority": "u=0, i",
                    "sec-ch-ua": '"Chromium";v="136", "Google Chrome";v="136", "Not.A/Brand";v="99"',
                    "sec-ch-ua-mobile": "?0",
                    "sec-ch-ua-platform": '"Windows"',
                    "sec-fetch-dest": "document",
                    "sec-fetch-mode": "navigate",
                    "sec-fetch-site": "none",
                    "sec-fetch-user": "?1",
                    "upgrade-insecure-requests": "1",
                    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36"
                },
                dont_filter=True,
                callback=self.parse_property
            )

    def parse_property(self, response: Response):
        output_item = response.meta.get('output_item')
        output_item['items_output']['main_data_property'] = extractor_info_property(response)
        
        yield scrapy.Request(
            url=path.join(
                output_item['items_output']['info_aux_property']['url'],
                ConfigPages.PATH_FEATURE_PROPERTY.value
            ),
            meta={'output_item': output_item},
            dont_filter=True,
            callback=self.parse_property_feature
        )

    def parse_property_feature(self, response: Response):
        output_item = response.meta.get('output_item')
        # extractor_feature_property(response.url)
        # extractor_rental_units(response.url)
        yield output_item


def extractor_info_property(response: Selector):
    return {
        "description_1": response.xpath(ConfigProperty.DESCRIPTION_1.value).getall(),
        "phone": response.xpath(ConfigProperty.PHONE.value).getall(),
        "email": response.xpath(ConfigProperty.MAIL.value).getall(),
        "address": response.xpath(ConfigProperty.ADDRESS.value).getall(),
        "description_2": response.xpath(ConfigProperty.DESCRIPTION_2.value).getall(),
        # "description_3": response.xpath(ConfigProperty.DESCRIPTION_3.value).getall(),
        "images": response.xpath(ConfigProperty.GALLERY.value).getall(),
    }

def extractor_feature_property(url_property: str):

    
    pass

def extractor_rental_units(url_property: str):
    pass

