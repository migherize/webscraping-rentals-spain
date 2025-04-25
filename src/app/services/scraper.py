import os
import json
import logging
import traceback
import subprocess

from typing import Callable, Dict, Optional, Tuple
from app.config.settings import EmailConfig, LOG_DIR, BASE_DIR, SCRAPY_DIR
from app.models.enums import URLs, Pages
from app.scrapy.common import initialize_scraping_context, initialize_scraping_context_maps


os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(funcName)s:%(lineno)d - %(message)s",
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

def run_webscraping(url: URLs, flag_refine=False) -> None:
    """
    Ejecuta Scrapy en un proceso separado usando subprocess con contexto adicional.

    Args:
        url (URLs): URL de la página que será scrapeada.
    """
    try:
        scrapy_path, context = get_path_and_context(url)
        if any([scrapy_path is None, context is None]):
            logger.error(f"No se encontró una araña para la URL: {url}")
            return None
        
        spider_name = f"{scrapy_path}_spider"
        output_folder_path = os.path.join(BASE_DIR, "logs", f"{scrapy_path}.log")        
        if os.path.exists(output_folder_path):
            os.remove(output_folder_path)

        logger.info(f"Ejecutando Scrapy con la araña: {spider_name}")
        execute_spider(scrapy_path, spider_name, output_folder_path, context, flag_refine)

    except Exception as e:
        logger.error(f"Error al hacer scraping para {url}: {str(e)}")
        logger.error(traceback.format_exc())


def get_path_and_context(url: URLs) -> Tuple[None | str | Callable]:
    """
    Obtiene la ruta como el contexto de la correspondiente aranha a ejecutar.
    Args:
        url (URLs): URL de la página que será scrapeada.
    """

    url_config: Optional[Dict[str, Callable]] = {
        URLs.flipcoliving: {
            "path": Pages.flipcoliving.value,
            "context": lambda: initialize_scraping_context(EmailConfig.FLIPCOLIVING)
        },
        URLs.somosalthena: {
            "path": Pages.somosalthena.value,
            "context": lambda: initialize_scraping_context(EmailConfig.SOMOSATHENEA)
        },
        URLs.yugo: {
            "path": Pages.yugo.value,
            "context": lambda: initialize_scraping_context_maps(EmailConfig.YUGO_MAPPING)
        },
        URLs.vita: {
            "path": Pages.vita.value,
            "context": lambda: initialize_scraping_context(EmailConfig.VITASTUDENTS)
        },
        URLs.nodis: {
            "path": Pages.nodis.value,
            "context": lambda: initialize_scraping_context(EmailConfig.NODIS)
        }
    }.get(url, None)

    if url_config is None:
        logger.error(f"No se encontró una araña para la URL: {url}")
        return None, None

    path_spider = url_config.get("path", None)
    if path_spider is None:
        logger.error('No se logró obtener el path. Error: %s', error)
        raise 'No se logró obtener el path'

    try:
        context = url_config.get("context")()
    except Exception as error:
        logger.error('No se logró obtener el context. Error: %s', error)
        raise 'No se logró obtener el context'

    return path_spider, context

def execute_spider(
        scrapy_path: str, 
        spider_name: str, 
        output_folder_path: str,
        context: Dict[str, list],
        flag_refine=False,
    ) -> None:
    try:
        command = [
                "scrapy", "crawl", spider_name,
                "-a", f"context={json.dumps(context)}",
                "-s", f"LOG_FILE={output_folder_path}",
                "-s", f"LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(funcName)s:%(lineno)d - %(message)s",
                "-s", f"LOG_LEVEL=INFO",
                "-s", f"LOG_DATEFORMAT=%Y-%m-%d %H:%M:%S",
        ]
        if flag_refine:
            command.extend(["-a", "refine=1"])
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=str(SCRAPY_DIR / scrapy_path / scrapy_path),
            encoding="utf-8",
        )

        logger.info(f"Scraping iniciado para {spider_name} (PID: {process.pid})")

        stdout, stderr = process.communicate()
        if stdout:
            logger.info(f"Scrapy Output para {spider_name}:\n{stdout}")
        if stderr:
            logger.error(f"Scrapy Error para {spider_name}:\n{stderr}")

    except Exception as error:
        logger.error('Problemas al ejecutar el spider. Error: %s', error)
        raise 'Problemas al ejecutar el spider'

    return None
