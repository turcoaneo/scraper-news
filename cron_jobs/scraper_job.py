import threading
import time

from app.utils.env_vars import SCRAPER_CONFIG
from service.util.scraper_runner import run_scraper


def run_job():
    article_time_cutoff = int(SCRAPER_CONFIG["article_time_cutoff"])
    run_scraper(article_time_cutoff)


def start_scraper_loop(interval_sec: int = 1200, is_looped: bool = True):
    from service.util.logger_util import get_logger
    logger = get_logger()
    logger.info(f"Starting scraper - looped: {is_looped}")

    def loop_cron_job():
        while True:
            run_job()
            time.sleep(interval_sec)
            if not is_looped:
                break

    threading.Thread(target=loop_cron_job, daemon=True).start()


if __name__ == "__main__":
    from distutils.util import strtobool

    looped = bool(strtobool(SCRAPER_CONFIG["looped"]))
    interval_seconds = int(SCRAPER_CONFIG["interval"])
    sleeping_time = int(SCRAPER_CONFIG["sleep_time"])

    try:
        start_scraper_loop(interval_seconds, looped)
        while True:
            time.sleep(sleeping_time)  # Keep main thread alive considering overall processing if looped=False
            if not looped:
                break
    except KeyboardInterrupt:
        print("Scraper loop stopped.")
