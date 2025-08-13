from scrapy import Spider
from eaie.items import EaieItem


class EaiePipeline:
    def __init__(self):
        self.item_count = 0

    def open_spider(self, spider: Spider):
        """ Operaciones antes de realizar la ejecucion de la arana """
        spider.logger.info("Spider opened: %s", spider.name)
        self.item_count = 0

    def process_item(self, item: EaieItem, spider: Spider):
        """ Operaciones que se pueden realizar cuando se obtiene un ITEM recolectado """
        self.item_count += 1
        if self.item_count % 10 == 0:
            spider.logger.info(f"Procesados {self.item_count} items")
        return item

    def close_spider(self, spider: Spider):
        """ Operaciones despues de finalizar la ejecucion de la arana """
        spider.logger.info("Spider finaled: %s.", spider.name)
        spider.logger.info(f"Total de items procesados: {self.item_count}")