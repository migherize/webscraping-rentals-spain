from os import path
from scrapy import Spider
from app.scrapy.common import save_to_json_file
from app.scrapy.flipcoliving.flipcoliving.flipcoliving.etl_flipcoliving import etl_data_flipcoliving


class FlipcolivingPipeline:
    def open_spider(self, spider: Spider):
        spider.logger.info("open_spider")
        self.json_path: str = path.join(
            spider.items_spider_output_document["output_folder"],
            spider.items_spider_output_document["file_name"],
        )
        self.items = []

    def process_item(self, item, spider: Spider) -> dict:
        self.items.append(dict(item))
        return item

    def close_spider(self, spider: Spider):
        spider.logger.info("close_spider")
        save_to_json_file(self.items, self.json_path)
        etl_data_flipcoliving(self.items, spider)
