import json
from app.scrapy.flipcoliving.spider import scrape_flipcoliving
from app.models.enums import URLs
import app.utils.constants as constants
from scrapy.crawler import CrawlerRunner
from crochet import setup

# from app.scrapy.flipcoliving.flipcoliving.flipcoliving_spider import FlipcolivingSpiderSpider
# from app.scrapy.somosalthena... import SomosalthenaSpider
# from app.scrapy.nodis... import NodisSpider

setup() 
runner = CrawlerRunner()

def run_webscraping(url: URLs) -> None:
    """
    Función para ejecutar el scraping y guardar los resultados.

    Args:
        url (str): URL de la página que será scrapeada.
    """
    try:
        if url == URLs.flipcoliving:
            # runner.crawl(FlipcolivingSpider, start_urls=[url.value])
            pass
        elif url == URLs.somosalthena:
            # runner.crawl(SomosAlthenaSpider, start_urls=[url.value])
            pass
        elif url == URLs.nodis:
            # runner.crawl(NodisSpider, start_urls=[url.value])
            pass
    except Exception as e:
        print(f"Error al hacer scraping: {str(e)}")

    except Exception as e:
        print(f"Error al hacer scraping: {str(e)}")
