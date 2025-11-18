# service/cluster_service.py

import json
from datetime import datetime
from zoneinfo import ZoneInfo

from app.config.loader import load_sites_from_config
from app.utils.env_vars import APP_ENV
from service.site_scraper import SiteScraper
from service.story_clusterer import StoryClusterer
from service.util.logger_util import get_logger
from service.util.path_util import PROJECT_ROOT
from service.s3_storage import S3Storage

logger = get_logger()
storage = S3Storage() if APP_ENV == "uat" else None


class ClusterService:

    @staticmethod
    def cluster_news(sites=None, minutes=1440):
        if sites is None:
            sites = ClusterService.load_sites()
        clusterer = StoryClusterer(sites, minutes, 0.3, 0.2)
        clusterer.cluster_stories()
        return clusterer.get_matched_clusters()

    @staticmethod
    def delete_old_csvs():
        if APP_ENV == "uat":
            logger.warning("CSV deletion skipped in UAT (S3 not supported)")
            return []
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
            serialized = json.dumps(jbf_data, ensure_ascii=False, indent=2).encode("utf-8")

            if APP_ENV == "uat":
                storage.save("buffer.json", serialized)
                logger.info("Saved JBF to S3")
                return "s3://{}/storage/buffer.json".format(storage.bucket)
            else:
                jbf_path = ClusterService.get_csv_buffer_result_path()
                with open(jbf_path, "wb") as f:
                    f.write(serialized)
                logger.info(f"Saved JBF to {jbf_path}")
                return jbf_path
        except Exception as e:
            logger.error(f"Failed to save JBF: {e}")
            return None

    @staticmethod
    def get_csv_buffer_result_path():
        return ClusterService.get_storage_path() / "buffer.json"

    @staticmethod
    def load_sites() -> list[SiteScraper]:
        sites = load_sites_from_config()
        total_traffic = sum(site.traffic for site in sites)
        for site in sites:
            site.compute_weight(total_traffic)
            site.load_recent_from_csv()
        return sites

    @staticmethod
    def get_storage_path():
        return PROJECT_ROOT / "storage"
