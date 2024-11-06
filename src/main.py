import os
import logging
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
logger.setLevel(logging.DEBUG)

app = FastAPI(
    title="API WebScrapingforRentalPlatforms",
    version="1.0",
    description="Esta API proporciona información sobre web scraping de diversas páginas web.",
)

@app.get("/")
def home_page():
    """
    Clasica pagina de inicio de Fastapi
    """
    logger.info(f"Home Page: WebScrapingforRentalPlatforms")
    return {"page": "API WebScrapingforRentalPlatforms", "Version": "1.0", "Update Date": "November 06 2024"}


@app.get("/scrape")
async def scrape_page(
    background_tasks: BackgroundTasks,
    page: models.Pages = Query(..., description="URL to be scraped"),
) -> Dict[str, str]:
    """
    Endpoint para iniciar el proceso de scraping en segundo plano.

    Args:
        url (str): URL de la página que será scrapeada.
        background_tasks (BackgroundTasks): Tareas en segundo plano para realizar scraping.

    Returns:
        dict: Mensaje confirmando que el scraping ha comenzado.
    """
 
    url = getattr(models.URLs, page.value).value
    logger.info(f"Solicitud de scraping recibida para la URL: {url}")

    try:
        background_tasks.add_task(scraper.run_webscraping, url)
        logger.info(f"Tarea de scraping iniciada en segundo plano para {url}")
        return {"message": "Scraping iniciado, consulta el estado más tarde."}
    except Exception as e:
        logger.error(f"Error al iniciar el scraping para {url}: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Error al iniciar el proceso de scraping."
        )


@app.get("/log_status/{spider_name}")
def check_log_status(spider_name: models.Pages) -> Dict[str, Any]:
    """
    Endpoint para verificar el estado del log de un spider basado en su nombre en el Enum Pages.

    Args:
        spider_name (models.Pages): Nombre del spider basado en el Enum Pages.

    Returns:
        dict: Estado de los logs del spider, incluyendo si está "running" o "finished".
    """
    log_path = f"logs/{spider_name.value}.log"
    logger.info(f"Verificando el estado del log para el spider: {spider_name.value}")

    if not os.path.isfile(log_path):
        logger.warning(f"Log no encontrado para el spider: {spider_name.value}")
        raise HTTPException(status_code=404, detail="Log no encontrado")

    try:
        with open(log_path, "r", encoding="utf-8") as log_file:
            log_content = log_file.readlines()

        # Chequear por "Iniciando la pipeline" y "close_spider" en el log
        is_running = any("Parseando" in line for line in log_content)
        is_finished = any("close_spider" in line for line in log_content)

        # Determinar el estado en base a la actividad en el log
        if is_running and not is_finished:
            status = "running"
        elif is_finished:
            status = "finished"
        else:
            status = "not_started"

        # Generar detalles de estado para el retorno
        details = {
            "status": status,
            "log_lines": log_content[-10:],  # Últimas líneas del log
        }

        logger.info(f"Estado del log de {spider_name.value}: {status}")
        return {"status": status, "details": details}

    except Exception as e:
        logger.error(f"Error al leer el archivo de log para {spider_name.value}: {str(e)}")
        raise HTTPException(
            status_code=500, detail="Error al procesar el archivo de log."
        )