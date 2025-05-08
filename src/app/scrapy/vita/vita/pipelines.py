from os import path
from scrapy import Spider
from app.scrapy.common import save_to_json_file
from app.scrapy.vita.vita.items import VitaItem
from app.scrapy.vita.vita.etl_vita import etl_data_vita


class VitaPipeline:
    def open_spider(self, spider: Spider) -> None:
        self.items = []
        self.output_path: str = path.join(
            spider.items_spider_output_document["output_folder"],
            spider.items_spider_output_document["file_name"],
        )

    def process_item(self, item: VitaItem, spider: Spider) -> dict:
        self.items.append(dict(item))
        return item

    def close_spider(self, spider: Spider) -> None:

        if spider.items_spider_output_document['refine'] == '1':
            spider.logger.info("- Refining data")
        else:
            spider.logger.info("- JSON file created with %d items.", len(self.items))
            save_to_json_file(self.items, self.output_path)

        etl_data_vita(self.items, spider.context, spider.logger)
        spider.logger.info("close_spider")
