# service/cluster_service.py
import json
import os
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from app.config.loader import load_sites_from_config
from service.story_clusterer import StoryClusterer
from service.util.logger_util import get_logger

logger = get_logger()


class ClusterService:

    @staticmethod
    def get_storage_path() -> Path:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        return Path(base_dir) / "storage"

    @staticmethod
    def cluster_news(sites=None, minutes=1440):
        if sites is None:
            sites = load_sites_from_config()
            for site in sites:
                site.load_recent_from_csv()

        total_traffic = sum(site.traffic for site in sites)
        for site in sites:
            site.compute_weight(total_traffic)

        clusterer = StoryClusterer(sites, minutes, 0.3, 0.2)
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
    def save_cluster_buffer(sites, minutes=1440):
        try:
            clusters = ClusterService.cluster_news(sites, minutes)
            ro_timestamp = datetime.now(ZoneInfo("Europe/Bucharest")).isoformat()
            jbf_data = {
                "timestamp": ro_timestamp,
                "clusters": clusters
            }

            jbf_path = ClusterService.get_csv_buffer_result_path()
            with open(jbf_path, "w", encoding="utf-8") as f:
                json.dump(jbf_data, f, ensure_ascii=False, indent=2)
            logger.info(f"Saved JBF to {jbf_path}")
            return jbf_path
        except Exception as e:
            logger.error(f"Failed to save JBF: {e}")
            return None

    @staticmethod
    def get_csv_buffer_result_path():
        return ClusterService.get_storage_path() / "buffer.json"
