import logging
import os
from fastapi import FastAPI
from app.api.router import router
import app.config.settings as settings
import sentry_sdk

SENTRY_ENABLE = os.getenv("SENTRY_ENABLE", "false").lower() == "true"
SENTRY_DSN = os.getenv("SENTRY_DSN", "")
SENTRY_ENV = os.getenv("SENTRY_ENV", "development")


if SENTRY_ENABLE and SENTRY_DSN:
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=SENTRY_ENV if SENTRY_ENV else "development",
        # Add data like request headers and IP for users,
        # see https://docs.sentry.io/platforms/python/data-management/data-collected/ for more info
        send_default_pii=True,
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for tracing.
        traces_sample_rate=1.0,
        _experiments={
            # Set continuous_profiling_auto_start to True
            # to automatically start the profiler on when
            # possible.
            "continuous_profiling_auto_start": True,
        },
    )

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
