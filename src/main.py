from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from typing import Dict, Any
import app.utils.constants as constants
import app.scrapy.flipcoliving as flipcoliving
import json
import os

app = FastAPI(
    title="API Flipcoliving",
    version="1.0",
    description="Esta API proporciona información sobre coliving, una comunidad de viviendas compartidas.",
)

@app.get("/")
async def root() -> Dict[str, str]:
    """
    Endpoint raíz para verificar si la API está funcionando correctamente.

    Returns:
        dict: Un mensaje de bienvenida indicando que la API está en funcionamiento.
    """
    return {"message": "flipcoliving"}

@app.get("/scrape")
async def scrape_flipcoliving(
    background_tasks: BackgroundTasks,
    url: str = Query(..., description="URL to be scraped")
) -> Dict[str, str]:
    """
    Endpoint para iniciar el proceso de scraping en segundo plano.

    Args:
        url (str): URL de la página que será scrapeada.
        background_tasks (BackgroundTasks): Tareas en segundo plano para realizar scraping.

    Returns:
        dict: Mensaje confirmando que el scraping ha comenzado.
    """
    # Añadir la tarea de scraping en segundo plano
    background_tasks.add_task(run_scraping, url)
    return {"message": "Scraping iniciado, consulta el estado más tarde."}



def run_scraping(url: str) -> None:
    """
    Función para ejecutar el scraping y guardar los resultados.

    Args:
        url (str): URL de la página que será scrapeada.
    """
    try:
        scraped_data = flipcoliving.scrape_flipcoliving(url)
        
        with open(constants.RESULTS_PATH, 'w') as f:
            json.dump(scraped_data, f)

    except Exception as e:
        print(f"Error al hacer scraping: {str(e)}")  # O manejar el error como prefieras


@app.get("/status")
async def get_scraping_status() -> Dict[str, Any]:
    """
    Endpoint para consultar el estado del último scraping.

    Returns:
        dict: Un diccionario con el estado del scraping y la ruta de los resultados.
    """
    if os.path.exists(constants.RESULTS_PATH):
        return {"status": "completed", "results_path": constants.RESULTS_PATH}
    else:
        return {"status": "not started or still running"}

@app.get("/results")
async def get_scraping_results() -> Dict[str, Any]:
    """
    Endpoint para obtener los resultados del scraping.

    Returns:
        dict: Los resultados del scraping en formato JSON.
    
    Raises:
        HTTPException: Si los resultados no están disponibles.
    """
    if os.path.exists(constants.RESULTS_PATH):
        with open(constants.RESULTS_PATH, 'r') as f:
            results = json.load(f)
        return {"data": results}
    else:
        raise HTTPException(status_code=404, detail="No hay resultados disponibles. Verifica el estado.")
