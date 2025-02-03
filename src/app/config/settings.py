import os
import json
from dotenv import load_dotenv
from pathlib import Path
from typing import Dict

# Cargar variables de entorno desde el archivo .env
load_dotenv()

# 📌 Rutas de trabajo
BASE_DIR = Path.cwd()
LOG_DIR = BASE_DIR / "logs"

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

# 📌 Configuración de Correos
class EmailConfig:
    FLIPCOLIVING = os.getenv("EMAIL_FLIPCOLIVING", "default_flipcoliving@example.com")
    SOMOSATHENEA = os.getenv("EMAIL_SOMOSATHENEA", "default_somosathenea@example.com")
    VITASTUDENTS = os.getenv("EMAIL_VITASTUDENTS", "default_vitastudents@example.com")
    YUGO_DEFAULT = os.getenv("EMAIL_YUGO_DEFAULT", "default_yugo@example.com")

    # Cargar JSON de EMAIL_MAPPING_YUGO de manera segura
    try:
        YUGO_MAPPING: Dict[str, str] = (os.getenv("EMAIL_MAPPING_YUGO", "{}"))
    except json.JSONDecodeError:
        YUGO_MAPPING = {}
        print("⚠️ Error al cargar EMAIL_MAPPING_YUGO. Se usará un diccionario vacío.")

# 📌 Configuración de Elementos JSON
class ElementsConfig:
    ELEMENTS_JSON = os.getenv("ELEMENTS_JSON", "{}")
