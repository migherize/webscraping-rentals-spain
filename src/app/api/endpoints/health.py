import logging
from fastapi import APIRouter

router = APIRouter()

logger = logging.getLogger(__name__)

@router.get("/", tags=["Health"])
def health_check():
    """
    Health check: Verifica si la API está operativa.
    """
    logger.info("Health check ejecutado: API funcional")
    return {
        "status": "OK",
        "message": "API WebScrapingforRentalPlatforms operativa",
    }

@router.get("/sentry-debug")
async def trigger_error():
    division_by_zero = 1 / 0