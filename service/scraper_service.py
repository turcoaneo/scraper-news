# service/cluster_service.py

import threading

from service.util.scraper_runner import run_scraper


class ScraperService:

    @staticmethod
    def scrape_sites_async() -> threading.Thread:
        thread = threading.Thread(target=run_scraper)
        thread.start()
        return thread
