from os import path
from scrapy import Spider
from app.scrapy.common import save_to_json_file
from app.scrapy.nodis.nodis.items import NodisItem
from app.scrapy.nodis.nodis.etl_nodis import etl_data_nodis


class NodisPipeline:
    def open_spider(self, spider: Spider) -> None:
        self.items = []
        self.output_path: str = path.join(
            spider.items_spider_output_document["output_folder"],
            spider.items_spider_output_document["file_name"],
        )

    def process_item(self, item: NodisItem, spider: Spider) -> dict:
        self.items.append(dict(item))
        return item

    def close_spider(self, spider: Spider) -> None:
        save_to_json_file(self.items, self.output_path)
        spider.logger.info('- JSON file created with %d items.', len(self.items))
        etl_data_nodis(self.items, spider)