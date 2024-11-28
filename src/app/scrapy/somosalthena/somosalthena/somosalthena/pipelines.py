import json
from os import path
from scrapy import Spider
from .utils import (
    get_data_json,
    parse_elements,
    retrive_lodgerin_property,
    retrive_lodgerin_rental_units,
    get_month
)

import app.utils.funcs as funcs
from app.models.schemas import (
    DatePayloadItem,
    mapping
)


class SomosalthenaPipeline:

    def open_spider(self, spider: Spider) -> None:
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
        write_to_json_file(self.json_path_no_refined, item["items_output"], spider)
        return item

    def close_spider(self, spider: Spider) -> None:
        output_data_json = get_data_json(spider, self.json_path_no_refined)
        write_to_json_file(self.json_path_refined, output_data_json, spider)

        elements_dict = parse_elements(spider.context[0], mapping)
        api_key = elements_dict["api_key"]["data"][0]["name"]
        
        print(f"api_key: {api_key}")

        for data in output_data_json:
            # Property
            data_property, cost = retrive_lodgerin_property(
                data, elements_dict
            )
            property_id = funcs.save_property(data_property, api_key)
            data_property.id = property_id
            # RentalUnit
            data_rental_units = retrive_lodgerin_rental_units(
                data_property, elements_dict, cost
            )
            rental_unit_id = funcs.save_rental_unit(data_rental_units, api_key)
            data_rental_units.id = rental_unit_id
            # Schedule
            # start_date, end_date, month = get_month()
            # calendar_unit = DatePayloadItem(
            #     summary=f"Blocked until {start_date}",
            #     description=f"Available from {month}",
            #     startDate=start_date,
            #     endDate=end_date,
            # )
            # funcs.check_and_insert_rental_unit_calendar(
            #     rental_unit_id, calendar_unit, api_key
            # )

def create_json_file(path_document: str, spider: Spider) -> None:
    """Creates an empty JSON file at the specified path.

    Args:
        path_document ath (str): The path where the JSON file will be created.
        spider (Spider): The instance of the spider for logging messages.
    """
    # Check if the file already exists
    if not path.exists(path_document):
        with open(path_document, "w") as file:
            json.dump([], file)  # Create an empty JSON file
        spider.logger.info("JSON file created at: %s", path_document)
    else:
        spider.logger.info("The file already exists at: %s", path_document)


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
