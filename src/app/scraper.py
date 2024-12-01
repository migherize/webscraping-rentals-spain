import logging
import os
import time
from socket import timeout

from crochet import setup, wait_for
from scrapy.crawler import CrawlerRunner
from twisted.internet.defer import inlineCallbacks

import app.utils.constants as constants
from app.models.enums import URLs
from app.scrapy.common import initialize_scraping_context
from app.scrapy.flipcoliving.flipcoliving.flipcoliving.spiders.flipcoliving_spider import (
    FlipcolivingSpiderSpider,
)
from app.scrapy.somosalthena.somosalthena.somosalthena.spiders.somosalthena_spider import (
    SomosalthenaSpiderSpider,
)

# from app.scrapy.nodis.nodis.nodis.spiders.nodis_spider import NodisSpider

os.makedirs(constants.LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            os.path.join(constants.LOG_DIR, "app.log"), mode="a", encoding="utf-8"
        ),
    ],
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

setup()
runner = CrawlerRunner()


@wait_for(timeout=600)
@inlineCallbacks
def run_webscraping(url: URLs) -> None:
    """
    Ejecuta el proceso de scraping y guarda los resultados.

    Args:
        url (URLs): URL de la página que será scrapeada.
    """
    try:
        context = ""
        if url == URLs.flipcoliving:
            context = initialize_scraping_context(constants.EMAIL_FLIPCOLIVING)
            yield runner.crawl(
                FlipcolivingSpiderSpider, start_urls=[url], context=context
            )

        elif url == URLs.somosalthena:
            context = initialize_scraping_context(constants.EMAIL_SOMOSATHENEA)
            yield runner.crawl(
                SomosalthenaSpiderSpider, start_urls=[url], context=context
            )

        elif url == URLs.nodis:
            # context = initialize_scraping_context(constants.EMAIL_NODIS)
            # yield runner.crawl(NodisSpider, start_urls=[url.value])
            pass

    except Exception as e:
        logger.info(f"Error al hacer scraping para {url}: {str(e)}")
