import logging
import os
from fastapi import FastAPI
from app.api.router import router
import app.config.settings as settings

os.makedirs(settings.LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(settings.LOG_DIR, "app.log"), mode="a", encoding="utf-8"),
    ],
)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

app = FastAPI(
    title="API WebScrapingforRentalPlatforms",
    version="1.0",
    description="API para web scraping de plataformas de alquiler.",
)

app.include_router(router)
