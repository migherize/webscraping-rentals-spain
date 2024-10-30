import os
from dotenv import load_dotenv

# Cargar .env
load_dotenv()
PATH_HOME = os.getcwd()
SCRAPINGBEE_API_KEY = os.getenv("SCRAPINGBEE_API_KEY")
LODGERIN_API_KEY = os.getenv("LODGERIN_API_KEY")
LODGERIN_API = os.getenv("LODGERIN_API")
MODELS_CONTRACT = "Medium-term"
BOOL_TRUE = True
BOOL_FALSE = False
COUNTRY = "Spain"
COUNTRY_CODE = "ES"
LANGUAGES = [1, 2]
CANCELLATION_POLICY = "standard"
RENTAL_TYPE = "individual"
PROPERTY_TYPE_ID = "Coliving"
RESULTS_PATH = "scraping_results.json"
INT_ZERO = 0
INT_ONE = 1