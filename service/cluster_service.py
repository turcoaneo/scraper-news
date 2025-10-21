# service/cluster_service.py

import os
import threading
from datetime import datetime
from pathlib import Path

from app.config.loader import load_sites_from_config
from service.story_clusterer import StoryClusterer
from service.util.scraper_runner import run_scraper


class ClusterService:

    @staticmethod
    def get_storage_path() -> Path:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return Path(base_dir) / "storage"

    @staticmethod
    def cluster_news():
        sites = load_sites_from_config()
        for site in sites:
            site.load_recent_from_csv()
        total_traffic = sum(site.traffic for site in sites)
        for site in sites:
            site.compute_weight(total_traffic)
        clusterer = StoryClusterer(sites, 360, 0.3, 0.2)
        clusterer.cluster_stories()
        return clusterer.get_matched_clusters()

    @staticmethod
    def delete_old_csvs():
        storage_path = ClusterService.get_storage_path()
        today_str = datetime.now().strftime("%Y%m%d")
        deleted = []
        for file in storage_path.glob("*.csv"):
            if today_str not in file.name:
                file.unlink()
                deleted.append(file.name)
        return deleted

    @staticmethod
    def scrape_sites_async() -> threading.Thread:
        thread = threading.Thread(target=run_scraper)
        thread.start()
        return thread
