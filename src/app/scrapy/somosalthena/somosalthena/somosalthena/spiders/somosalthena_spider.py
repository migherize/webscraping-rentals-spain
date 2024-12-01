# coding=utf-8
import re
from ast import literal_eval
from os import path
from pathlib import Path

import scrapy

from app.scrapy.common import read_json

from .. import items
from ..constants_spider import item_custom_settings, item_input_output_archive
from ..enum_path import RegexProperty

# import app.utils.constants as constants
# import app.models.enums as models


# scrapy crawl somosalthena_spider -a refine=0
# scrapy crawl somosalthena_spider -a refine=1


class SomosalthenaSpiderSpider(scrapy.Spider):
    name = "somosalthena_spider"
    custom_settings = item_custom_settings

    def __init__(self, context=None, *args, **kwargs):

        super(SomosalthenaSpiderSpider, self).__init__(*args, **kwargs)

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
        # self.context = context
        self.context = read_json()

    def start_requests(self):
        """
        Inicio de la pagina principal
        """

        if self.items_spider_output_document["refine"] == "1":
            self.logger.info("Proceso de Refinado")
            return None

        url = "https://somosalthena.com/inmuebles/"

        yield scrapy.Request(
            url=url,
        )

    def parse(self, response):

        all_data = re.search(RegexProperty.ALL_DATA_API.value, response.text)

        if not all_data:
            self.logger.warning("No se presenta una API en la url: %s", response.url)
            return None

        all_data = literal_eval(all_data.group(1))

        if not all_data:
            self.logger.warning("No se logro la obtencion del JSON")
            return None

        item = items.SomosalthenaItem()

        item["items_output"] = all_data
        yield item
