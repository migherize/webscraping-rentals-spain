import json
from os import path
from scrapy import Spider
from .items import YugoItem

import app.utils.funcs as funcs
from app.scrapy.common import parse_elements
import app.utils.constants as constants
from app.models.schemas import ContractModel, Property, RentalUnits,  DatePayloadItem, mapping
from .utils import (
    retrive_lodgerin_property,
    # retrive_lodgerin_rental_units,
    # check_and_insert_rental_unit_calendar
)

def save_to_json_file(data: list, output_path: str) -> None:
    """
    Writes a list of data to a JSON file.

    Args:
        data (list): The data to be written to the JSON file.
        output_path (str): The file path where the JSON file will be saved.
    """
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)

class YugoPipeline:
    def open_spider(self, spider: Spider) -> None:
        """
        Initializes the pipeline by setting up storage for items.
        """
        self.items = []
        self.output_path: str = path.join(
            spider.items_spider_output_document["output_folder"],
            spider.items_spider_output_document["file_name"],
        )
        spider.logger.info('- Pipeline initialized. JSON output path: %s', self.output_path)

    def process_item(self, item: YugoItem, spider: Spider) -> dict:
        """
        Processes each item and stores it in the in-memory list.
        Converts the Scrapy Item to a dictionary before storing.
        """
        # Convert YugoItem to a dictionary
        self.items.append(dict(item))
        return item

    def close_spider(self, spider: Spider) -> None:
        """
        Writes all items to the JSON file and closes the pipeline.
        """
        save_to_json_file(self.items, self.output_path)
        spider.logger.info('- JSON file created with %d items.', len(self.items))

        elements_dict = parse_elements(spider.context[0], mapping)
        api_key = elements_dict["api_key"]["data"][0]["name"]

        for data in self.items:
            # Property
            data_property = retrive_lodgerin_property(data, elements_dict)
            property_id = funcs.save_property(data_property, api_key)
            data_property.id = property_id
