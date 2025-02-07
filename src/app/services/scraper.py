import logging
import os
import subprocess
import json
import traceback

from app.config.settings import EmailConfig, LOG_DIR, BASE_DIR, SCRAPY_DIR
from app.models.enums import URLs, Pages
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

def run_webscraping(url: URLs) -> None:
    """
    Ejecuta Scrapy en un proceso separado usando subprocess con contexto adicional.

    Args:
        url (URLs): URL de la página que será scrapeada.
    """
    try:
        context = None
        scrapy_path = None

        if url == URLs.flipcoliving:
            scrapy_path = Pages.flipcoliving.value
            context = initialize_scraping_context(EmailConfig.FLIPCOLIVING)

        elif url == URLs.somosalthena:
            scrapy_path = Pages.somosalthena.value
            context = initialize_scraping_context(EmailConfig.SOMOSATHENEA)

        elif url == URLs.yugo:
            scrapy_path = Pages.yugo.value
            email_map = json.loads(EmailConfig.YUGO_MAPPING)
            context = initialize_scraping_context_maps(email_map)

        elif url == URLs.vita:
            scrapy_path = Pages.vita.value
            context = initialize_scraping_context(EmailConfig.VITASTUDENTS)

        else:
            logger.error(f"No se encontró una araña para la URL: {url}")
            return

        spider_name = f"{scrapy_path}_spider"
        output_folder_path = os.path.join(BASE_DIR, "logs", f"{scrapy_path}.log")
        logger.info(f"Ejecutando Scrapy con la araña: {spider_name}")

        if os.path.exists(output_folder_path):
            os.remove(output_folder_path)

        process = subprocess.Popen(
            ["scrapy", "crawl", spider_name, "-a", f"context={json.dumps(context)}", "-s", f"LOG_FILE={output_folder_path}"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(SCRAPY_DIR / scrapy_path / scrapy_path)
        )

        logger.info(f"Scraping iniciado para {spider_name} (PID: {process.pid})")

        stdout, stderr = process.communicate()
        if stdout:
            logger.info(f"Scrapy Output para {spider_name}:\n{stdout}")
        if stderr:
            logger.error(f"Scrapy Error para {spider_name}:\n{stderr}")

    except Exception as e:
        logger.error(f"Error al hacer scraping para {url}: {str(e)}")
        logger.error(traceback.format_exc())