import os
import logging
from crochet import setup, wait_for
from twisted.internet.defer import inlineCallbacks
from scrapy.crawler import CrawlerRunner
from app.models.enums import URLs
import app.utils.constants as constants

from app.scrapy.flipcoliving.flipcoliving.flipcoliving.spiders.flipcoliving_spider import FlipcolivingSpiderSpider
# from app.scrapy.somosalthena.somosalthena.somosalthena.spiders.somosalthena_spider import SomosAlthenaSpider
# from app.scrapy.nodis.nodis.nodis.spiders.nodis_spider import NodisSpider

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


setup()
runner = CrawlerRunner()

@wait_for(timeout=60)
@inlineCallbacks
def run_webscraping(url: URLs) -> None:
    """
    Ejecuta el proceso de scraping y guarda los resultados.

    Args:
        url (URLs): URL de la página que será scrapeada.
    """
    try:
        if url == URLs.flipcoliving:
            yield runner.crawl(FlipcolivingSpiderSpider, start_urls=[url.value])

        elif url == URLs.somosalthena:
            # yield runner.crawl(SomosAlthenaSpider, start_urls=[url.value])
            pass

        elif url == URLs.nodis:
            # yield runner.crawl(NodisSpider, start_urls=[url.value])
            pass

    except Exception as e:
        logger.info(f"Error al hacer scraping para {url.name}: {str(e)}")
