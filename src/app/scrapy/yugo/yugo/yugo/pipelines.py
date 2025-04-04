from os import path
from scrapy import Spider
from app.scrapy.common import save_to_json_file
from app.scrapy.yugo.yugo.yugo.items import YugoItem
from app.scrapy.yugo.yugo.yugo.etl_yugo import etl_data_yugo


class YugoPipeline:
    def open_spider(self, spider: Spider) -> None:
        """
        Initializes the pipeline by setting up storage for items.
        """
        spider.logger.info("open_spider")
        self.items = []
        self.output_path: str = path.join(
            spider.items_spider_output_document["output_folder"],
            spider.items_spider_output_document["file_name"],
        )
        spider.logger.info(
            "- Pipeline initialized. JSON output path: %s", self.output_path
        )

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
        if spider.items_spider_output_document['refine'] == '1':
            spider.logger.info("- Refining data")
        else:
            spider.logger.info("- JSON file created with %d items.", len(self.items))
            save_to_json_file(self.items, self.output_path)

        # etl_data_yugo(spider, self.output_path)

        spider.logger.info("close_spider")
