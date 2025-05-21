import re
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
    ConfigRentalUnits
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
            info_city = {
                'state': response_state.xpath(ConfigCity.TITLE.value).get(),
                'url': response_state.xpath(ConfigCity.URL.value).get(),
                'description': response_state.xpath(ConfigCity.DESCRIPTION.value).get(),
            }
            yield scrapy.Request(
                info_city['url'],
                meta={'info_city': info_city},
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
        
        info_city = response.meta.get('info_city')
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
                    'info_city': info_city,
                    'info_property': info_property,
                }
                yield output_item
                continue

            if re.search(r'precios?', info_property['url']):
                info_property['url'] = "/".join(info_property['url'].split('/')[0:-2])
            
            output_item['items_output'] = {
                'info_city': info_city,
                'info_aux_property': info_property,
            }

            yield scrapy.Request(
                info_property['url'],
                meta={'output_item': output_item},
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
        output_item['items_output']['main_data_property'] |= extractor_feature_property(response)
        
        url_rental = response.xpath(ConfigPages.PATH_RENTAL_UNITS.value).get()

        if url_rental is None:
            yield output_item
            return None
            
        yield scrapy.Request(
            url=url_rental,
            meta={'output_item': output_item},
            dont_filter=True,
            callback=self.parse_property_rental_units
        )


    def parse_property_rental_units(self, response: Response):
        output_item = response.meta.get('output_item')

        search_data_rental = response.xpath(ConfigRentalUnits.PIVOTE.value)

        if not search_data_rental:
            self.logger.info('Sin rental units para: %s', response.url)
            yield output_item
            return None

        output_item['items_output']['main_data_rental'] = {
            "url_rental_units": response.url,
            "all_rental_units": []
        }
        
        all_rental_units = []
        for position_rental, search_rental in enumerate(search_data_rental):
            # Informacion principal del rental
            aux_search_images = search_rental.xpath(ConfigRentalUnits.PIVOTE_IMAGES.value)
            output_main_data_rental = {
                "name_1": search_rental.xpath(ConfigRentalUnits.NAME_1.value).getall(),
                "name_2": search_rental.xpath(ConfigRentalUnits.NAME_2.value).getall(),
                "description": search_rental.xpath(ConfigRentalUnits.DESCRIPTION.value).getall(),
                "features": search_rental.xpath(ConfigRentalUnits.FEATURES.value).getall(),
                "images": aux_search_images.xpath(ConfigRentalUnits.IMAGES.value).getall(),
                "all_types": []
            }
            check_search_type = ConfigRentalUnits.PIVOTE_TYPE_RENTAL.value + f"[{position_rental + 1}]/div"
            for info_type_rental in response.xpath(check_search_type):
                # Informacion de los tipos que existen para dicho rental
                all_types = {
                    'type_and_description_rental_unit': info_type_rental.xpath(ConfigRentalUnits.TYPE_AND_DESCRIPTION_RENTAL_UNIT.value).getall(),
                    'more_information': info_type_rental.xpath(ConfigRentalUnits.MORE_INFORMATION.value).getall(),
                    'cost_and_reservation': info_type_rental.xpath(ConfigRentalUnits.COST_AND_RESERVATION.value).getall(),
                }

                if all_types['type_and_description_rental_unit'] == []:
                    print('check_search_type:', [check_search_type], [info_type_rental], response.url)

                output_main_data_rental['all_types'].append(all_types)

            all_rental_units.append(output_main_data_rental)

        output_item['items_output']['main_data_rental']["all_rental_units"] = all_rental_units

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

def extractor_feature_property(response: Selector):

    output = {
        'feature': response.xpath(ConfigProperty.FEATURE.value).getall()
    }
    # TODO: Elimminar los que tengan el *
    return output

