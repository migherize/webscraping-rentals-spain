import os
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

# Directorios y configuraciones generales
PATH_HOME = os.getcwd()
LOG_DIR = os.path.join(PATH_HOME, "logs")

# Valores constantes del negocio
MODELS_CONTRACT = "Medium-term"
BOOL_TRUE = True
BOOL_FALSE = False
COUNTRY = "Spain"
COUNTRY_CODE = "ES"
LANGUAGES = [1, 2]
CANCELLATION_POLICY = "standard"
RENTAL_TYPE = "individual"
PROPERTY_TYPE_ID = "Coliving"
INT_ZERO = 0
INT_ONE = 1

# Variables de entorno (con valores por defecto si no están definidas)
SCRAPINGBEE_API_KEY = os.getenv("SCRAPINGBEE_API_KEY", "default_scrapingbee_key")
ELEMENTS_JSON = os.getenv("ELEMENTS_JSON", "{}")  # JSON vacío como fallback

LODGERIN_API_KEY = os.getenv("LODGERIN_API_KEY", "default_lodgerin_key")
LODGERIN_API = os.getenv("LODGERIN_API", "https://default-lodgerin-api.com")
LODGERIN_INTERNAL = os.getenv("LODGERIN_INTERNAL", "https://default-internal.com")
TOKEN_API_INTERNAL = os.getenv("TOKEN_API_INTERNAL", "default_token")
EMAIL_FLIPCOLIVING = os.getenv("EMAIL_FLIPCOLIVING", "default_flipcoliving@example.com")
EMAIL_SOMOSATHENEA = os.getenv("EMAIL_SOMOSATHENEA", "default_somosathenea@example.com")
EMAIL_MAPPING_YUGO = os.getenv("EMAIL_MAPPING_YUGO", "{}")  # JSON vacío como fallback
EMAIL_YUGO_DEFAULT = os.getenv("EMAIL_YUGO_DEFAULT", "default_yugo@example.com")
LODGERIN_MAPS_INTERNAL = os.getenv("LODGERIN_MAPS_INTERNAL", "https://default-maps.com")
