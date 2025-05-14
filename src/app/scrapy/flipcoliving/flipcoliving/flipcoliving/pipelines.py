from os import path
from scrapy import Spider
from app.scrapy.common import save_to_json_file
from app.scrapy.flipcoliving.flipcoliving.flipcoliving.etl_flipcoliving import etl_data_flipcoliving


class FlipcolivingPipeline:
    def open_spider(self, spider: Spider):
        spider.logger.info("open_spider")
        self.items = []
        self.output_path: str = path.join(
            spider.items_spider_output_document["output_folder"],
            spider.items_spider_output_document["file_name"],
        )
        spider.logger.info(
            "- Pipeline initialized. JSON output path: %s", self.output_path
        )

    def process_item(self, item, spider: Spider) -> dict:
        self.items.append(dict(item))
        return item

    def close_spider(self, spider: Spider):

        if spider.items_spider_output_document['refine'] == '1':
            spider.logger.info("- Refining data")
        else:
            spider.logger.info("- JSON file created with %d items.", len(self.items))
            save_to_json_file(self.items, self.output_path)

        etl_data_flipcoliving(self.output_path, spider.logger, spider.context)
        spider.logger.info("close_spider")
