import os

from dotenv import load_dotenv

load_dotenv()

APP_ENV = os.environ.get("APP_ENV", "local")

SCRAPER_CONFIG = {
    "looped": os.environ.get("SCRAPER_JOB_LOOPED", "False"),
    "sleep_time": os.environ.get("SCRAPER_SLEEPING_TIME", 400),
    "interval": os.environ.get("SCRAPER_INTERVAL_SECONDS", 5),
}
