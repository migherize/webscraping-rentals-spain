from os import path
from scrapy import Spider
from app.scrapy.common import save_to_json_file
from app.scrapy.livensaliving.livensaliving.items import LivensalivingItem


class LivensalivingPipeline:
    def open_spider(self, spider: Spider) -> None:
        self.items = []
        self.output_path: str = path.join(
            spider.items_spider_output_document["output_folder"],
            spider.items_spider_output_document["file_name"],
        )

    def process_item(self, item: LivensalivingItem, spider: Spider) -> dict:
        self.items.append(dict(item))
        return item

    def close_spider(self, spider: Spider) -> None:

        if spider.items_spider_output_document['refine'] == '1':
            spider.logger.info("- Refining data")
        else:
            spider.logger.info("- JSON file created with %d items.", len(self.items))
            save_to_json_file(self.items, self.output_path)

        # etl_data_livensaliving(self.output_path, spider, spider.logger)
        spider.logger.info("close_spider")
