import os
import json
import logging
from enum import Enum
from typing import Dict, Any
from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
import app.utils.constants as constants
import app.models.enums as models
import app.scraper as scraper

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

app = FastAPI(
    title="API WebScrapingforRentalPlatforms",
    version="1.0",
    description="Esta API proporciona información sobre web scraping de diversas páginas web.",
)


@app.get("/scrape")
async def scrape_page(
    background_tasks: BackgroundTasks,
    url: models.URLs = Query(..., description="URL to be scraped"),
) -> Dict[str, str]:
    """
    Endpoint para iniciar el proceso de scraping en segundo plano.

    Args:
        url (str): URL de la página que será scrapeada.
        background_tasks (BackgroundTasks): Tareas en segundo plano para realizar scraping.

    Returns:
        dict: Mensaje confirmando que el scraping ha comenzado.
    """
    logger.info(f"Solicitud de scraping recibida para la URL: {url.name}")

    try:
        background_tasks.add_task(scraper.run_webscraping, url)
        logger.info(f"Tarea de scraping iniciada en segundo plano para {url.name}")
        return {"message": "Scraping iniciado, consulta el estado más tarde."}
    except Exception as e:
        logger.error(f"Error al iniciar el scraping para {url.name}: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Error al iniciar el proceso de scraping."
        )


@app.get("/log_status/{spider_name}")
def check_log_status(spider_name: models.Pages) -> Dict[str, str]:
    """
    Endpoint para verificar el estado del log de un spider basado en su nombre en el Enum URLs.

    Args:
        spider_name (URLs): Nombre del spider basado en el Enum URLs.

    Returns:
        dict: Estado de los logs del spider.
    """
    log_path = f"logs/{spider_name.name}/{spider_name.name}_spider.log"
    logger.info(f"Verificando el estado del log para el spider: {spider_name.name}")

    if not os.path.exists(log_path):
        logger.warning(f"Log no encontrado para el spider: {spider_name.name}")
        raise HTTPException(status_code=404, detail="Log no encontrado")

    with open(log_path, "r", encoding="utf-8") as log_file:
        errors = [line for line in log_file if "ERROR" in line]

    if errors:
        logger.info(
            f"Se encontraron {len(errors)} errores en el log de {spider_name.name}"
        )
        return {"status": "error", "details": f"{len(errors)} errores encontrados"}
    else:
        logger.info(f"No se encontraron errores en el log de {spider_name.name}")
        return {"status": "ok", "details": "No se encontraron errores"}
