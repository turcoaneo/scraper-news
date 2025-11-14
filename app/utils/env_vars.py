# app/utils/env_vars.py

import os

from dotenv import dotenv_values


def clean_list(raw):
    return [x.strip() for x in raw.split(",") if x.strip()]


# Load base + environment-specific config
APP_ENV = os.environ.get("APP_ENV", "test")
base_env = dotenv_values(".env")
env_specific = dotenv_values(f".env.{APP_ENV}")
merged = {**base_env, **env_specific, **os.environ}  # system vars override all

LOG_LEVEL = merged.get("LOG_LEVEL", "warning")
LLM_ROOT = merged.get("LLM_ROOT", "local")
HF_TOKEN = merged.get("HF_TOKEN", None)

SCRAPER_CONFIG = {
    "looped": merged.get("SCRAPER_JOB_LOOPED", "False") == "True",
    "sleep_time": int(merged.get("SCRAPER_SLEEPING_TIME", 400)),
    "interval": int(merged.get("SCRAPER_INTERVAL_SECONDS", 5)),
    "article_time_cutoff": int(merged.get("SCRAPER_ARTICLE_TIME_CUTOFF", 1440)),
}

FILTER_PLACE_KEYS = {
    "place": clean_list(merged.get("FILTER_PLACES", "")),
    "including": clean_list(merged.get("FILTER_INCLUDING", "")),
    "excluding": clean_list(merged.get("FILTER_EXCLUDING", "")),
}
