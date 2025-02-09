# coding=utf-8
import re
import json
import logging
from os import path
from pathlib import Path

import scrapy
import requests
from scrapy import Selector

from .. import items
from ..enum_path import XpathGeneralColiving


class FlipcolivingSpiderSpider(scrapy.Spider):
    name = "flipcoliving_spider"
    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "AUTOTHROTTLE_ENABLED": True,
        "LOG_LEVEL": "INFO",
        # "LOG_FORMAT": '%(asctime)s [%(levelname)s] %(message)s',
        # "LOG_DATEFORMAT": '%Y-%m-%d %H:%M:%S',
        # "LOGFILE": 'scrapy_log.log'
        # "LOG_FILE":"scrapy_log.txt",
        # "LOG_LEVEL":"DEBUG",
        # "LOG_LEVEL": "INFO",
    }

    def __init__(self, context=None, *args, **kwargs):

        super(FlipcolivingSpiderSpider, self).__init__(*args, **kwargs)

        item_input_output_archive: dict[str, str] = {
            "output_folder_path": "./",
            "output_folder_name": "process_data",
            "output_folder_name": "data",
            "file_name": f"flipcoliving.json",
            "processed_name": f"flipcoliving_refined.json",
            "refine": '1',
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

        # Obtener LOG_FILE desde los argumentos
        log_path = kwargs.pop("LOG_FILE", None)
        self.logger.info(f"log_path: {log_path}")
        self.context = json.loads(context) if isinstance(context, str) else {}

    def start_requests(self):
        """
        Inicio de la pagina principal
        """

        if self.items_spider_output_document['refine'] == '1':
            self.logger.info('Inicia proceso de refinado')
            return []

        url = "https://flipcoliving.com/"

        yield scrapy.Request(
            url=url,
        )

    def parse(self, response):
        """
        Obtener las URL de las Ciudades
        """

        cities_url = response.xpath(XpathGeneralColiving.CITIES_URL.value)

        if not cities_url:
            logging.info("No se obtuvieron las URL de las ciudades")
            return None

        # Recorrer ciudades
        for city_url in cities_url:

            aux_city_url = city_url.get()
            aux_city_url = response.url + aux_city_url
            if aux_city_url is None:
                logging.info(
                    "Se obtuvo un valor para la url de la ciudad: %s", aux_city_url
                )
                continue

            city_name = re.sub(r"[^A-Za-z]", " ", aux_city_url.split("-")[-1]).strip()
            yield scrapy.Request(
                url=aux_city_url,
                dont_filter=True,
                meta={
                    "city_name": city_name,
                    "aux_city_url": aux_city_url,
                },
                callback=self.parse_all_colivings,
            )

    def parse_all_colivings(self, response):
        """
        Obtener las URL de los coliving
        """

        colivings_url = response.xpath(XpathGeneralColiving.COLIVING_URL.value)

        if not colivings_url:
            logging.info("No se obtuvieron las URL de los colivings")
            return None

        items_meta = response.meta

        # Recorrer los Coliving
        for coliving_url in colivings_url:

            coliving_url = coliving_url.get()

            if coliving_url is None:
                logging.info(
                    "Se obtuvo un valor para el coliving: %s", coliving_url
                )
                continue

            coliving_name = re.sub(
                r"[^A-Za-z]", " ", coliving_url.split("/")[-2]
            ).strip()

            yield scrapy.Request(
                url=coliving_url,
                dont_filter=True,
                meta={
                    "city_name": items_meta["city_name"],
                    "aux_city_url": items_meta["aux_city_url"],
                    "coliving_url": coliving_url,
                    "coliving_name": coliving_name,
                },
                callback=self.parse_coliving,
            )

    def parse_coliving(self, response):
        """
        Extraer la data del coliving
        """

        items_meta = response.meta

        # ------------------------------------------------------------

        items_output = {
            # Extraccion de las imagenes principales
            "all_firts_imagenes": XpathGeneralColiving.FIRST_IMAGENES.value,
            # Extraccion del nombre del Coliving
            "parse_coliving_name": XpathGeneralColiving.COLIVING_NAME.value,
            # Extraccion del Banner: Ubicacion, rango de precio, area, habitaciones
            "banner_features": XpathGeneralColiving.BANNER_FEATURES.value,
            # Extraccion de la descriccion
            "parse_description": XpathGeneralColiving.ABOUT_THE_HOME.value,
            # Extraccion de los features
            "all_features": XpathGeneralColiving.FEATURES.value,
            # Extraccion de las URL tours
            "all_url_tour": XpathGeneralColiving.TOUR_URL.value,
            # Extraccion de las URL tours
            "latitude": XpathGeneralColiving.LATITUDE.value,
            # Extraccion de las URL tours
            "longitude": XpathGeneralColiving.LONGITUDE.value,
        }

        for key, value_data_1 in items_output.items():
            items_output[key] = response.xpath(value_data_1).getall()
            if items_output[key]:
                items_output[key] = self.check_data_object(items_output[key])
        items_output["all_firts_imagenes"] = self.remove_duplicate_urls(
            items_output["all_firts_imagenes"]
        )
        items_output["all_firts_imagenes"] = self.get_all_imagenes(
            items_output["all_firts_imagenes"]
        )
        items_output["city_name"] = items_meta["city_name"]
        items_output["aux_city_url"] = items_meta["aux_city_url"]
        items_output["coliving_url"] = items_meta["coliving_url"]
        items_output["coliving_name"] = items_meta["coliving_name"]
        # ------------------------------------------------------------
        # Extraccion informacion: The rooms and The Unit

        items_rental_units = []

        type_name_rental_unit = response.xpath(
            XpathGeneralColiving.TYPE_NAME_RENTAL_UNIT.value
        ).get()

        if type_name_rental_unit == "The Unit":
            # Unico rental unit

            data_rental_unit = {
                # tipo de rental unit
                "type_name_rental_unit": [type_name_rental_unit],
                # Nombre del rental unit
                "name_rental_unit": response.xpath(
                    XpathGeneralColiving.NAME_RENTAL_UNIT.value
                ).getall(),
                # Estado del rental unit
                "available_rental_unit": response.xpath(
                    XpathGeneralColiving.AVAILABLE_RENTAL_UNIT.value
                ).getall(),
                # Rango de precio y are del rental unit
                "data_rental_unit": response.xpath(
                    XpathGeneralColiving.DATA_RENTAL_UNIT.value
                ).getall(),
                # Extraccion de las imagenes del rental unit
                "imagenes_rental_unit": response.xpath(
                    XpathGeneralColiving.IMAGENES_RENTAL_UNIT.value
                ).getall(),
            }
            data_rental_unit["imagenes_rental_unit"] = self.remove_duplicate_urls(
                data_rental_unit["imagenes_rental_unit"]
            )
            items_rental_units.append(data_rental_unit)

        elif type_name_rental_unit == "The Rooms":
            # Multiples rental unit

            all_rental_unit = response.xpath(
                "//div[contains(@class, 'theRooms__slider')]/div"
            )

            if not all_rental_unit:
                items_rental_units.append({})
            else:
                for value_data_2 in all_rental_unit:

                    data_rental_unit = {
                        # tipo de rental unit
                        "type_name_rental_unit": [type_name_rental_unit],
                        # Nombre del rental unit
                        "name_rental_unit": value_data_2.xpath(
                            XpathGeneralColiving.MULTIPLE_NAME_RENTAL_UNIT.value
                        ).getall(),
                        # Estado del rental unit
                        "available_rental_unit": value_data_2.xpath(
                            XpathGeneralColiving.MULTIPLE_AVAILABLE_RENTAL_UNIT.value
                        ).getall(),
                        # Rango de precio y are del rental unit
                        "data_rental_unit": value_data_2.xpath(
                            XpathGeneralColiving.MULTIPLE_DATA_RENTAL_UNIT.value
                        ).getall(),
                        # Extraccion de las imagenes del rental unit
                        "imagenes_rental_unit": value_data_2.xpath(
                            XpathGeneralColiving.MULTIPLE_IMAGENES_RENTAL_UNIT.value
                        ).getall(),
                    }
                    data_rental_unit["imagenes_rental_unit"] = (
                        self.remove_duplicate_urls(
                            data_rental_unit["imagenes_rental_unit"]
                        )
                    )

                    items_rental_units.append(data_rental_unit)

        else:
            logging.info(
                "No presenta rental_units el coliving: %s. Ciudad: %s. URL: %s",
                items_meta["coliving_name"],
                items_meta["city_name"],
                response.url,
            )

        items_rental_units = self.check_data_object(items_rental_units)
        all_url = response.xpath(XpathGeneralColiving.LANGUAGE_URL.value).getall()

        items_output["rental_units"] = items_rental_units

        for index_language, url_language in enumerate(all_url):

            if index_language == 0:
                # ingles
                continue

            description = self.parse_coliving_language(url_language)
            items_output["parse_description"].append(description)

        item = items.FlipcolivingItem()
        item["items_output"] = items_output
        self.logger.info('Extraida propiedad: %s', items_output['coliving_name'])
        yield item

    def parse_coliving_language(self, url):
        response_with_requests = requests.get(url)
        response_with_scrapy = Selector(text=response_with_requests.text)
        description = response_with_scrapy.xpath(
            XpathGeneralColiving.ABOUT_THE_HOME.value
        ).get()
        return description

    def check_data_object(self, data_object: list) -> list:

        # Utilizado para los Rental Units
        if isinstance(data_object[0], dict):

            # Recorrer todos los rental units
            for index, rental_unit in enumerate(data_object):
                rental_unit: dict
                for key, value_data in rental_unit.items():
                    data_object[index][key] = list(map(self.check_data, value_data))
                    data_object[index][key] = list(
                        filter(None, data_object[index][key])
                    )
            return data_object

        # Solo listas
        if isinstance(data_object[0], str):
            data_object = list(map(self.check_data, data_object))
            data_object = list(filter(None, data_object))
            return data_object

    def check_data(self, data) -> list:

        data = re.sub(r"\t|\n|\r|\xa0", "  ", data).strip()
        data = re.sub(r"\s{2,}", " ", data).strip()
        return data

    def remove_duplicate_urls(self, url_list: list) -> list:
        cleaned_urls = []
        seen = set()

        for url in url_list:
            clean_url = re.sub(r"-\d+x\d+\.jpg", ".jpg", url.split()[0])

            if clean_url not in seen:  # If the item has not been seen
                seen.add(clean_url)  # Add it to the set
                cleaned_urls.append(clean_url)  # Add it to the result list

        return cleaned_urls

    def get_all_imagenes(self, space_images: list) -> list[dict]:
        all_imagenes = []

        if not space_images:
            return []
        for index, value in enumerate(space_images):
            cover = True if index == 0 else False
            all_imagenes.append(
                {
                    "image": value,
                    "isCover": cover,
                }
            )
        return all_imagenes
