# coding=utf-8
import re
import json
import scrapy
from ast import literal_eval
from os import path
from pathlib import Path
from app.scrapy.somosalthena.somosalthena.somosalthena import items


class SomosalthenaSpiderSpider(scrapy.Spider):
    name = "somosalthena_spider"
    custom_settings = {
        "ROBOTSTXT_OBEY": False,
        "AUTOTHROTTLE_ENABLED": True,
        "LOG_LEVEL": "INFO",
    }

    def __init__(self, context=None, *args, **kwargs):

        super(SomosalthenaSpiderSpider, self).__init__(*args, **kwargs)

        item_input_output_archive: dict[str, str] = {
            "output_folder_path": "./",
            "output_folder_name": r"somosalthena",
            "file_name": f"somosalthena.json",
            "processed_name": "somosalthena_refined.json",
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

        # -----------------------------------------------------------------
        # if folder not exists create one
        Path(self.items_spider_output_document["output_folder"]).mkdir(
            parents=True, exist_ok=True
        )
        self.context = json.loads(context) if context else {}

    def start_requests(self):
        """
        Inicio de la pagina principal
        """
        if self.items_spider_output_document['refine'] == '1':
            self.logger.info("Proceso de refinado para: %s", self.name)
            return []

        url = "https://somosalthena.com/inmuebles/"

        yield scrapy.Request(
            url=url,
        )

    def parse(self, response):

        all_data = re.search(r"const postData = (\[.+\])", response.text)

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
