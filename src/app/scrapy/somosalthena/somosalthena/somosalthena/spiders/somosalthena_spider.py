# coding=utf-8
import os
import re
import scrapy
import logging
import requests
import json

from os import path
from pathlib import Path
from ast import literal_eval

from .. import items
from ..constants_spider import item_custom_settings, item_input_output_archive
from ..enum_path import RegexProperty

# import app.utils.constants as constants
# import app.models.enums as models



class SomosalthenaSpiderSpider(scrapy.Spider):
    name = "somosalthena_spider"
    custom_settings = item_custom_settings
    def __init__(self, *args, **kwargs):

        super(SomosalthenaSpiderSpider, self).__init__(*args, **kwargs)

        # -----------------------------------------------------------------
        # Ruta de la carpeta donde se almancera la data extraida
        self.output_folder_path = kwargs.pop(
            'output_folder_path', item_input_output_archive['output_folder_path']
        )
        # Nombre de la carpeta donde se almacenara la data extraida
        self.output_folder_name = kwargs.pop(
            'output_folder_name', item_input_output_archive['output_folder_name']
        )
        # Path de la carpeta salida
        self.output_folder = path.join(
            self.output_folder_path, self.output_folder_name
        )

        # -----------------------------------------------------------------
        # Nombre del documento con la data extraida sin refinar
        self.output_filename = kwargs.pop(
            'file_name', item_input_output_archive['file_name']
        )
        # Nombre del documento con la data extraida refinada
        self.output_filename_processed = kwargs.pop(
            'processed_name', item_input_output_archive['processed_name']
        )
        
        # -----------------------------------------------------------------
        # if folder not exists create one
        Path(self.output_folder).mkdir(
            parents=True, exist_ok=True
        )

    def start_requests(self):

        """
        Inicio de la pagina principal
        """

        url = 'https://somosalthena.com/inmuebles/'

        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
            "accept-language": "es-419,es;q=0.9,en-US;q=0.8,en;q=0.7",
            "cache-control": "max-age=0",
            "priority": "u=0, i",
            "sec-ch-ua": "\"Chromium\";v=\"130\", \"Google Chrome\";v=\"130\", \"Not?A_Brand\";v=\"99\"",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "\"Windows\"",
            "sec-fetch-dest": "document",
            "sec-fetch-mode": "navigate",
            "sec-fetch-site": "same-origin",
            "sec-fetch-user": "?1",
            "upgrade-insecure-requests": "1"
        }
        
        yield scrapy.Request(
            url=url,
            headers=headers,
        )

    def parse(self, response):

        all_data = re.search(RegexProperty.ALL_DATA_API.value, response.text)

        if not all_data:
            self.logger.warning('No se presenta una API en la url: %s', response.url)
            return None
        
        all_data = literal_eval(all_data.group(1))

        if not all_data:
            self.logger.warning('No se logro la obtencion del JSON')
            return None

        try:
            path_document_API = os.path.join(self.output_folder, self.output_filename)
            with open(path_document_API,'w') as json_file:
                json.dump(all_data, json_file, indent=4)
        except Exception as error:
            self.logger.error('No se logro guardar la data en un archivo .json')
            self.logger.error('Error: "%s"', str(error))