import os
from dotenv import load_dotenv
from pathlib import Path
from typing import Dict
from ast import literal_eval

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# 📌 Rutas de trabajo
BASE_DIR = Path.cwd()
LOG_DIR = BASE_DIR / "logs"

# 📌 Verificar qué directorio de Scrapy existe
SCRAPY_DIRS = [BASE_DIR / "src/app/scrapy", BASE_DIR / "app/scrapy"]
SCRAPY_DIR = next((path for path in SCRAPY_DIRS if path.exists()), None)

# 📌 Constantes globales
class GlobalConfig:
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

# 📌 Configuración de APIs de Lodgerin
class LodgerinConfig:
    API_KEY = os.getenv("LODGERIN_API_KEY", "default_lodgerin_key")
    API_URL = os.getenv("LODGERIN_API", "https://default-lodgerin-api.com")
    INTERNAL_URL = os.getenv("LODGERIN_INTERNAL", "https://default-internal.com")
    MAPS_INTERNAL_URL = os.getenv("LODGERIN_MAPS_INTERNAL", "https://default-maps.com")

# 📌 Tokens y Seguridad
class TokenConfig:
    API_INTERNAL = os.getenv("TOKEN_API_INTERNAL", "default_token")
    USERNAME_NAFSA = os.getenv("USERNAME_NAFSA", "default_username_nafsa_token")
    PASSWORD_NAFSA = os.getenv("PASSWORD_NAFSA", "default_password_nafsa_token")


# 📌 Configuración de Correos
class EmailConfig:
    FLIPCOLIVING = os.getenv("EMAIL_FLIPCOLIVING", "default_flipcoliving@example.com")
    SOMOSATHENEA = os.getenv("EMAIL_SOMOSATHENEA", "default_somosathenea@example.com")
    VITASTUDENTS = os.getenv("EMAIL_VITASTUDENTS", "default_vitastudents@example.com")
    YUGO_DEFAULT = os.getenv("EMAIL_YUGO_DEFAULT", "default_yugo@example.com")
    NODIS = os.getenv("EMAIL_NODIS", "default_nodis@example.com")

    # Cargar JSON de EMAIL_MAPPING_YUGO de manera segura
    try:
        YUGO_MAPPING: str = os.getenv("EMAIL_MAPPING_YUGO", "{}")
        YUGO_MAPPING: Dict[str, str] = literal_eval(YUGO_MAPPING)
    except Exception as error:
        YUGO_MAPPING = {}
        print("⚠️ Error al cargar EMAIL_MAPPING_YUGO. Se usará un diccionario vacío. Error:", error)

# 📌 Configuración de Elementos JSON
class ElementsConfig:
    ELEMENTS_JSON = os.getenv("ELEMENTS_JSON", "{}")
    PATH_LOGS = os.getenv("LOGS", "./logs")
    PATH_DATA = os.getenv("DATA", "./data")
