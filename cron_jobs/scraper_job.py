import threading
import time

from service.util.scraper_runner import run_scraper


def run_job():
    run_scraper()


def start_scraper_loop(interval_seconds: int = 1200, looped: bool = True):
    def loop():
        while True:
            run_job()
            time.sleep(interval_seconds)
            if not looped:
                break

    threading.Thread(target=loop, daemon=True).start()


if __name__ == "__main__":
    looped = False
    start_scraper_loop(6, looped)
    try:
        while True:
            time.sleep(400)  # Keep main thread alive
            if not looped:
                break
    except KeyboardInterrupt:
        print("Scraper loop stopped.")
