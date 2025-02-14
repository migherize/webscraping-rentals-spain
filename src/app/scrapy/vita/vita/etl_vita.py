import json
from scrapy import Spider
from app.scrapy.common import parse_elements
from app.models.schemas import mapping


def etl_data_vita(items: list[dict], spider: Spider):
    pass
    # TODO: Revisar ETL flip_coliving


def test_etl_data_vita(items: list[dict]):
    for index, item in enumerate(items):
        pass


if __name__ == '__main__':
    test_etl_data_vita([{}])