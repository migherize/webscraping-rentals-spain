import json
from os import path
from scrapy import Spider

import app.scrapy.funcs as funcs
from app.scrapy.yugo.yugo.yugo.items import YugoItem
from app.scrapy.common import parse_elements, create_json, read_json
from app.models.schemas import mapping
from app.scrapy.yugo.yugo.yugo.utils import (
    retrive_lodgerin_property,
    retrive_lodgerin_rental_units
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
        list_api_key = elements_dict["api_key"]["data"]

        for data in self.items:
            data = data["items_output"]
            # Property
            data_property, api_key = retrive_lodgerin_property(data, elements_dict, list_api_key)
            if api_key:
                property_id = funcs.save_property(data_property, api_key)
                print("property_id", property_id)
                data_property.id = property_id
                create_json(data_property)
                # RentalUnit
                if data["all_rental_units"]:
                    data_rental_units, calendar_unit_list = retrive_lodgerin_rental_units(
                        data_property, elements_dict, data["all_rental_units"]
                    )
                    list_rental_unit_id = []
                    print("data_rental_units",len(data_rental_units))
                    for rental_unit in data_rental_units:
                        create_json(rental_unit)
                        rental_unit_id = funcs.save_rental_unit(rental_unit, api_key)
                        print("rental_unit_id", rental_unit_id)
                        rental_unit.id = rental_unit_id
                        list_rental_unit_id.append(rental_unit)

                    # schedule
                    for rental_id, calendar_unit in zip(
                        list_rental_unit_id, calendar_unit_list
                    ):
                        if calendar_unit.startDate == "None":
                            continue
                        funcs.check_and_insert_rental_unit_calendar(rental_id, calendar_unit, api_key)

                    for calendar_unit in calendar_unit_list:
                        create_json(calendar_unit)



if __name__=="__main__":
    elements_dict = parse_elements(read_json(), mapping)
    list_api_key = elements_dict["api_key"].data

    try:
        with open("/Users/mherize/squadmakers/logderin/WebScrapingforRentalPlatforms/src/app/scrapy/yugo/yugo/data/data/yugo.json", "r", encoding="utf-8") as file:
            items = json.load(file)
    
    except FileNotFoundError:
        print(f"Error: El archivo no se encontró.")

    for data in items:
        data = data["items_output"]
        # Property
        data_property, api_key = retrive_lodgerin_property(data, elements_dict, list_api_key)
        if api_key:
            property_id = funcs.save_property(data_property, api_key)
            print("property_id", property_id)
            data_property.id = property_id
            create_json(data_property)
            # RentalUnit
            if data["all_rental_units"]:
                data_rental_units, calendar_unit_list = retrive_lodgerin_rental_units(
                    data_property, elements_dict, data["all_rental_units"]
                )
                list_rental_unit_id = []
                print("data_rental_units",len(data_rental_units))
                for rental_unit in data_rental_units:
                    create_json(rental_unit)
                    rental_unit_id = funcs.save_rental_unit(rental_unit, api_key)
                    print("rental_unit_id", rental_unit_id)
                    rental_unit.id = rental_unit_id
                    list_rental_unit_id.append(rental_unit)

                # schedule
                for rental_id, calendar_unit in zip(
                    list_rental_unit_id, calendar_unit_list
                ):
                    print("calendar_unit", calendar_unit)
                    print("rental_id.id", rental_id.id)
                    if calendar_unit.startDate == "None":
                        continue
                    funcs.check_and_insert_rental_unit_calendar(rental_id.id, calendar_unit, api_key)

                for calendar_unit in calendar_unit_list:
                    create_json(calendar_unit)