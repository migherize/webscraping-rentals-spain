import logging
import os
from typing import Any, Dict
from fastapi import APIRouter, BackgroundTasks, HTTPException, Query
import app.models.enums as models
import app.services.scraper as scraper

router = APIRouter()

logger = logging.getLogger(__name__)

@router.get("/scrape")
async def scrape_page(
    background_tasks: BackgroundTasks,
    page: models.Pages = Query(..., description="Página a scrapeear"),
) -> Dict[str, str]:
    """
    Inicia el proceso de scraping en segundo plano.
    """
    url = getattr(models.URLs, page.value).value
    logger.info(f"Solicitud de scraping recibida para la URL: {url}")

    try:
        background_tasks.add_task(scraper.run_webscraping, url)
        logger.info(f"Tarea de scraping iniciada en segundo plano para {url}")
        return {"message": "Scraping iniciado, consulta el estado más tarde."}
    except Exception as e:
        logger.error(f"Error al iniciar el scraping: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al iniciar el scraping.")

@router.get("/log_status/{spider_name}")
def check_log_status(spider_name: models.Pages) -> Dict[str, Any]:
    """
    Verifica el estado del log de un spider basado en el Enum Pages.
    """
    log_path = f"logs/{spider_name.value}.log"
    logger.info(f"Verificando el estado del log para el spider: {spider_name.value}")

    if not os.path.isfile(log_path):
        logger.warning(f"Log no encontrado para: {spider_name.value}")
        raise HTTPException(status_code=404, detail="Log no encontrado")

    try:
        with open(log_path, "r", encoding="utf-8") as log_file:
            log_content = log_file.readlines()

        is_running = any("Parseando" in line for line in log_content)
        is_finished = any("close_spider" in line for line in log_content)

        status = "running" if is_running and not is_finished else "finished" if is_finished else "not_started"

        return {"status": status, "details": log_content[-10:]}  # Últimas 10 líneas

    except Exception as e:
        logger.error(f"Error al leer el log: {str(e)}")
        raise HTTPException(status_code=500, detail="Error al procesar el archivo de log.")
