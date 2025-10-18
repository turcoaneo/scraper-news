import threading
import time

from service.util.scraper_runner import run_scraper


def run_job():
    print("Running scraper job")
    run_scraper()


def start_scraper_loop(interval_seconds: int = 120):
    def loop():
        while True:
            run_job()
            time.sleep(interval_seconds)

    threading.Thread(target=loop, daemon=True).start()


if __name__ == "__main__":
    start_scraper_loop(6)
    try:
        while True:
            time.sleep(1)  # Keep main thread alive
    except KeyboardInterrupt:
        print("Scraper loop stopped.")
