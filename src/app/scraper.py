import os
import logging
from socket import timeout
import time
from crochet import setup, wait_for
from twisted.internet.defer import inlineCallbacks
from scrapy.crawler import CrawlerRunner
from app.models.enums import URLs
import app.utils.constants as constants

from app.scrapy.flipcoliving.flipcoliving.flipcoliving.spiders.flipcoliving_spider import FlipcolivingSpiderSpider
from app.scrapy.somosalthena.somosalthena.somosalthena.spiders.somosalthena_spider import SomosalthenaSpiderSpider
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

def initialize_scraping_context():
    """
    Realiza la inicialización previa al scraping, como obtener API keys, tokens y configuraciones.
    
    Returns:
        dict: Diccionario con datos inicializados como API key, tokens y otros valores.
    """
    try:
        apikey = "obtained_api_key"
        token_actualizado = "updated_token"
        servicios = ["servicio1", "servicio2"]

        return {
            "apikey": apikey,
            "token": token_actualizado,
            "servicios": servicios
        }
    except Exception as e:
        logger.error(f"Error durante la inicialización del contexto de scraping: {str(e)}")
        raise


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
        context = initialize_scraping_context()
        logger.info(f"Contexto inicializado: {context}")
        
        if url == URLs.flipcoliving:
            yield runner.crawl(FlipcolivingSpiderSpider, start_urls=[url], context=context)

        elif url == URLs.somosalthena:
            yield runner.crawl(SomosalthenaSpiderSpider, start_urls=[url], context=context)

        elif url == URLs.nodis:
            # yield runner.crawl(NodisSpider, start_urls=[url.value])
            pass

    except Exception as e:
        logger.info(f"Error al hacer scraping para {url}: {str(e)}")
