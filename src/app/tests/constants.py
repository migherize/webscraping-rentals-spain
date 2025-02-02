import os

from dotenv import load_dotenv

# Cargar .env
load_dotenv()
PATH_HOME = os.getcwd()

API_KEY = os.getenv("LODGERIN_API_KEY")
API_BASE_URL = os.getenv("LODGERIN_API")

HEADERS = {"x-access-apikey": API_KEY, "x-access-lang": "en"}
