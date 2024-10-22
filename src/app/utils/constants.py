import os
from dotenv import load_dotenv

# Cargar .env
load_dotenv()
PATH_HOME = os.getcwd()
SCRAPINGBEE_API_KEY = os.getenv("SCRAPINGBEE_API_KEY")
LODGERIN_API = os.getenv("LODGERIN_API")
RESULTS_PATH = "scraping_results.json"
