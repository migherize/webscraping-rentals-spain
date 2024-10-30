import json
from app.scrapy.flipcoliving.spider import scrape_flipcoliving
from app.models.enums import URLs
import app.utils.constants as constants

def run_webscraping(url: URLs) -> None:
    """
    Función para ejecutar el scraping y guardar los resultados.

    Args:
        url (str): URL de la página que será scrapeada.
    """
    try:
        # scraped_data = None

        print("url.value: ",url.value)
        
        if url == URLs.flipcoliving:
            scrape_flipcoliving(url.value)
        elif url == URLs.somosalthena:
            # somosalthena.scrape_somosalthena(url.value)
            pass
        elif url == URLs.nodis:
            # scraped_data = nodis.scrape_nodis(url.value)
            pass

        # if scraped_data is not None:
        #     with open(constants.RESULTS_PATH, "w") as f:
        #         json.dump(scraped_data, f)
        # else:
        #     raise ValueError("No se pudo obtener datos scrapeados.")

    except Exception as e:
        print(f"Error al hacer scraping: {str(e)}")
