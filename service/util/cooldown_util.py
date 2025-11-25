import json
import threading
from datetime import datetime

from app.utils.env_vars import APP_ENV, S3_BUCKET, S3_PREFIX
from service.util.logger_util import get_logger
from service.util.path_util import PROJECT_ROOT
from service.util.s3_util import S3Util

logger = get_logger()

_last_scrape_times: dict[str, datetime] = {}
_lock = threading.Lock()
COOLDOWN_FILE = PROJECT_ROOT / "storage" / "cooldown.json"

s3_util = S3Util(S3_BUCKET, S3_PREFIX)


def load_cooldowns():
    if APP_ENV == "uat":
        _load_cooldowns_s3()
    else:
        _load_cooldowns_local()


def save_cooldowns():
    if APP_ENV == "uat":
        _save_cooldowns_s3()
    else:
        _save_cooldowns_local()


def get_last_scrape_times() -> dict[str, datetime]:
    return _last_scrape_times


def update_scrape_time(site_name: str, timestamp: datetime):
    with _lock:
        _last_scrape_times[site_name] = timestamp
        save_cooldowns()


def _load_cooldowns_local():
    global _last_scrape_times
    if COOLDOWN_FILE.exists():
        try:
            with open(COOLDOWN_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                _last_scrape_times = {
                    site: datetime.fromisoformat(ts) for site, ts in data.items()
                }
                logger.info("Restore last scrape times from local JSON file.")
        except Exception as e:
            logger.warning(f"Failed to load cooldowns locally: {e}")
            _last_scrape_times = {}


def _save_cooldowns_s3():
    try:
        payload = {site: ts.isoformat() for site, ts in _last_scrape_times.items()}
        s3_util.write_json(f"{S3_PREFIX}/cooldown.json", payload)
        logger.info("Persist last scrape times to S3 JSON file.")
    except Exception as e:
        logger.warning(f"Failed to save cooldowns to S3: {e}")


def _save_cooldowns_local():
    try:
        with open(COOLDOWN_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {site: ts.isoformat() for site, ts in _last_scrape_times.items()},
                f,
            )
            logger.info("Persist last scrape times to local JSON file.")
    except Exception as e:
        logger.warning(f"Failed to save cooldowns locally: {e}")


def _load_cooldowns_s3():
    global _last_scrape_times
    data = s3_util.read_json(f"{S3_PREFIX}/cooldown.json")
    if data:
        try:
            _last_scrape_times = {
                site: datetime.fromisoformat(ts) for site, ts in data.items()
            }
            logger.info("Restore last scrape times from S3 JSON file.")
        except Exception as e:
            logger.warning(f"Failed to parse cooldowns from S3: {e}")
            _last_scrape_times = {}
    else:
        _last_scrape_times = {}
