from fastapi import APIRouter
from app.api.endpoints import health, scraper

router = APIRouter()
router.include_router(health.router, tags=["Health"])
router.include_router(scraper.router, prefix="/scraper", tags=["Scraper"])
