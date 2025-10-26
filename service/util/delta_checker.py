# service/util/delta_checker.py

import csv
from datetime import datetime
from pathlib import Path

from service.site_scraper import SiteScraper
from service.util.csv_util import is_filtered
from service.util.logger_util import get_logger
from service.util.path_util import PROJECT_ROOT

logger = get_logger()


class DeltaChecker:

    @staticmethod
    def has_delta(site: SiteScraper, csv_path=None) -> bool:
        if csv_path is None:
            today_str = datetime.now().strftime('%Y%m%d')
            filename = f"{site.name}_{today_str}.csv"
            csv_path = Path(PROJECT_ROOT) / "storage" / filename

        if not csv_path.exists():
            logger.info(f"[DeltaChecker] No previous CSV for {site.name}, assuming delta.")
            return True

        seen = set()
        with open(csv_path, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)  # read everything while file is open

        seen = set((row["timestamp"], row["url"]) for row in rows)

        from app.utils.env_vars import FILTER_PLACE_KEYS
        for article in site.articles:
            if is_filtered(article, FILTER_PLACE_KEYS) or DeltaChecker.is_foreign_article(article, site.name):
                continue
            key = (article.timestamp.isoformat(), article.url)
            if key not in seen:
                logger.info(f"[DeltaChecker] Key not found: {key} vs seen keys: {list(seen)[:5]}")
                logger.info(f"[DeltaChecker] New article for {site.name}: {article.title} - {article.timestamp}")
                return True

            # Now safe to check title changes
            for row in rows:
                if row["url"] == article.url and row["title"] != article.title:
                    logger.info(f"[DeltaChecker] Title changed for {site.name}: {article.title}")
                    return True

        return False

    @staticmethod
    def is_foreign_article(article, site_name):
        from urllib.parse import urlparse
        domain = urlparse(article.url).netloc
        return site_name not in domain

    @staticmethod
    def any_site_has_delta(sites: list[SiteScraper]) -> bool:
        for site in sites:
            if DeltaChecker.has_delta(site):
                return True
        return False
