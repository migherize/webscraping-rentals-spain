import json
from os import path
from scrapy import Spider
from .items import YugoItem


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
        self.items = []  # Temporary in-memory storage for items
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
