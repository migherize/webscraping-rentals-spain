import json
from os import path
from scrapy import Spider
from .items import VitastudentItem


class VitastudentPipeline:
    def open_spider(self, spider: Spider) -> None:
        self.items = []
        self.output_path: str = path.join(
            spider.items_spider_output_document["output_folder"],
            spider.items_spider_output_document["file_name"],
        )
        spider.logger.info('- Pipeline initialized. JSON output path: %s', self.output_path)

    def process_item(self, item: VitastudentItem, spider: Spider) -> dict:
        self.items.append(dict(item))
        return item

    def close_spider(self, spider: Spider) -> None:
        save_to_json_file(self.items, self.output_path)
        spider.logger.info('- JSON file created with %d items.', len(self.items))


def save_to_json_file(data: list, output_path: str) -> None:
    with open(output_path, "w", encoding="utf-8") as json_file:
        json.dump(data, json_file, ensure_ascii=False, indent=4)
