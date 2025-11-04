# app/utils/env_vars.py

import os

from dotenv import load_dotenv

load_dotenv()


def clean_list(raw):
    return [x.strip() for x in raw.split(",") if x.strip()]


APP_ENV = os.environ.get("APP_ENV", "local")
LOGGING_DEBUG_LEVEL = clean_list(os.environ.get("LOGGING_DEBUG_LEVEL", "local, dev"))

SCRAPER_CONFIG = {
    "looped": os.environ.get("SCRAPER_JOB_LOOPED", "False"),
    "sleep_time": int(os.environ.get("SCRAPER_SLEEPING_TIME", 400)),
    "interval": int(os.environ.get("SCRAPER_INTERVAL_SECONDS", 5)),
    "article_time_cutoff": int(os.environ.get("SCRAPER_ARTICLE_TIME_CUTOFF", 1440)),
}

FILTER_PLACE_KEYS = {
    "place": clean_list(os.environ.get("FILTER_PLACES", "")),
    "including": clean_list(os.environ.get("FILTER_INCLUDING", "")),
    "excluding": clean_list(os.environ.get("FILTER_EXCLUDING", "")),
}
