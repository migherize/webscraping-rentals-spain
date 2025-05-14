from fastapi import APIRouter
from app.api.endpoints import health, scrapy

router = APIRouter()
router.include_router(health.router, tags=["Health"])
router.include_router(scrapy.router, prefix="/scraper", tags=["Scraper"])
