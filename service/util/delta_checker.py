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
    def get_site_deltas(site: SiteScraper, csv_path=None) -> tuple:
        if csv_path is None:
            today_str = datetime.now().strftime('%Y%m%d')
            filename = f"{site.name}_{today_str}.csv"
            csv_path = Path(PROJECT_ROOT) / "storage" / filename

        previous_articles = {}
        if csv_path.exists():
            with open(csv_path, encoding="utf-8") as f:
                reader: csv.DictReader = csv.DictReader(f)
                for row in reader:
                    key = row["url"]
                    row["timestamp"] = datetime.fromisoformat(row["timestamp"])
                    previous_articles[key] = row

        current_articles = {
            article.url: article
            for article in site.articles
            if
            not is_filtered(article, site.filter_place_keys) and not DeltaChecker.is_foreign_article(article, site.name)
        }

        new = []
        updated = []
        removed = []

        def timestamps_equal(t1, t2):
            return t1.replace(microsecond=0, tzinfo=None) == t2.replace(microsecond=0, tzinfo=None)

        for url, article in current_articles.items():
            if url not in previous_articles:
                new.append(article)
            else:
                prev = previous_articles[url]
                if prev["title"] != article.title or not timestamps_equal(prev["timestamp"], article.timestamp):
                    logger.info(f"""[DeltaChecker] Update for {article.url}: \
                    {prev['title']} vs {article.title} \
                    {prev['timestamp']} vs {article.timestamp}""")
                    updated.append(article)

        for url in previous_articles:
            if url not in current_articles:
                removed.append(previous_articles[url])  # raw dict row

        logger.info(f"[DeltaChecker] {site.name} → New: {len(new)}, Updated: {len(updated)}, Removed: {len(removed)}")
        current_articles_map = {
            "new": new,
            "updated": updated,
            "removed": removed
        }
        return previous_articles, current_articles_map

    @staticmethod
    def is_foreign_article(article, site_name):
        from urllib.parse import urlparse
        domain = urlparse(article.url).netloc
        return site_name not in domain

    @staticmethod
    def get_all_deltas(sites: list[SiteScraper]) -> dict:
        return {
            site.name: DeltaChecker.get_site_deltas(site)
            for site in sites
        }
