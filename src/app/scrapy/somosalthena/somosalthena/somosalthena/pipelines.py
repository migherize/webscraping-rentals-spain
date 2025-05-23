import json
from os import path

from scrapy import Spider

import app.scrapy.funcs as funcs
from app.models.schemas import mapping
from app.scrapy.common import parse_elements, create_json
from app.models.enums import Pages
from app.scrapy.somosalthena.somosalthena.somosalthena.utils import (
    get_data_json,
    retrive_lodgerin_property,
    retrive_lodgerin_rental_units,
)
from app.models.enums import Pages
from app.services.csvexport import CsvExporter


class SomosalthenaPipeline:

    def open_spider(self, spider: Spider) -> None:
        spider.logger.info("open_spider")
        self.json_path_no_refined: str = path.join(
            spider.items_spider_output_document["output_folder"],
            spider.items_spider_output_document["file_name"],
        )
        self.json_path_refined: str = path.join(
            spider.items_spider_output_document["output_folder"],
            spider.items_spider_output_document["processed_name"],
        )
        create_json_file(self.json_path_no_refined, spider)
        create_json_file(self.json_path_refined, spider)

    def process_item(self, item: dict, spider: Spider) -> dict:
        print("********* process_item *********")
        write_to_json_file(self.json_path_no_refined, item["items_output"], spider)
        return item

    def close_spider(self, spider: Spider) -> None:
        print("********* close_spider *********")
        output_data_json = get_data_json(self.json_path_no_refined)
        write_to_json_file(self.json_path_refined, output_data_json, spider)
        elements_dict = parse_elements(spider.context, mapping)
        api_key = elements_dict["api_key"].data[0].name
        exporter = CsvExporter(Pages.somosalthena.value)


        for data in output_data_json:
            # Property
            data_property, cost = retrive_lodgerin_property(data, elements_dict)
            create_json(data_property,Pages.somosalthena.value)
            property_id = funcs.save_property(data_property, api_key)
            data_property.id = property_id
            # RentalUnit
            data_rental_units = retrive_lodgerin_rental_units(
                data_property, elements_dict, cost
            )
            create_json(data_rental_units,Pages.somosalthena.value)
            rental_unit_id = funcs.save_rental_unit(data_rental_units, api_key)
            data_rental_units.id = rental_unit_id
            exporter.process_and_export_to_csv(data_property, data_rental_units)
        
        spider.logger.info("close_spider")
           

def create_json_file(path_document: str, spider: Spider) -> None:
    """Creates an empty JSON file at the specified path.

    Args:
        path_document ath (str): The path where the JSON file will be created.
        spider (Spider): The instance of the spider for logging messages.
    """
    # Check if the file already exists
    with open(path_document, "w") as file:
        json.dump([], file)  # Create an empty JSON file
    spider.logger.info("JSON file created at: %s", path_document)


def write_to_json_file(path_document: str, items: list[dict], spider: Spider) -> None:
    """Writes a list of dictionaries to the specified JSON file.

    Args:
        path_document (str): The path of the JSON file where data will be written.
        items (list[dict]): List of dictionaries to add to the JSON file.
        spider (Spider): The instance of the spider for logging messages.
    """
    try:
        with open(path_document, "r+") as file:
            # Load the current content of the file
            content = json.load(file)
            # Add new items to the existing content
            content.extend(items)
            # Move the cursor to the beginning of the file to overwrite it
            file.seek(0)
            json.dump(content, file, indent=4)  # Write the new content
            file.truncate()  # Remove any old content that remains
        spider.logger.info("Items written to the file: %s", path_document)

    except Exception as e:
        spider.logger.error("An error occurred while writing to the file: %s", e)
