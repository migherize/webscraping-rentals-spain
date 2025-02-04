import logging
import os
import json
import traceback
from crochet import setup, wait_for
from scrapy.crawler import CrawlerRunner
from twisted.internet.defer import inlineCallbacks
from app.config.settings import EmailConfig, LOG_DIR
from app.models.enums import URLs
from app.scrapy.common import initialize_scraping_context, initialize_scraping_context_maps

# Spider
from app.scrapy.flipcoliving.flipcoliving.flipcoliving.spiders.flipcoliving_spider import FlipcolivingSpiderSpider
from app.scrapy.somosalthena.somosalthena.somosalthena.spiders.somosalthena_spider import SomosalthenaSpiderSpider
from app.scrapy.yugo.yugo.yugo.spiders.yugo_spider import YugoSpiderSpider
from app.scrapy.vitastudent.vitastudent.spiders.vitastudent_spider import VitastudentSpiderSpider

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(
            os.path.join(LOG_DIR, "app.log"), mode="a", encoding="utf-8"
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
            context = initialize_scraping_context(EmailConfig.FLIPCOLIVING)
            yield runner.crawl(
                FlipcolivingSpiderSpider, start_urls=[url], context=context
            )

        elif url == URLs.somosalthena:
            context = initialize_scraping_context(EmailConfig.SOMOSATHENEA)
            yield runner.crawl(
                SomosalthenaSpiderSpider, start_urls=[url], context=context
            )

        elif url == URLs.yugo:
            email_map = json.loads(EmailConfig.YUGO_MAPPING)
            context = initialize_scraping_context_maps(email_map)
            # yield runner.crawl(YugoSpiderSpider, start_urls=[url.value], context=context)
        
        elif url == URLs.vita:
            context = initialize_scraping_context(EmailConfig.VITASTUDENTS)
            yield runner.crawl(VitastudentSpiderSpider, start_urls=[url.value], context=context)


    except Exception as e:
        logger.error(f"Error al hacer scraping para {url}: {str(e)}")
        logger.error(traceback.format_exc())
