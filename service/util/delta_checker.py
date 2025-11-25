import csv
from datetime import datetime
from pathlib import Path

from app.utils.env_vars import APP_ENV, S3_PREFIX, S3_BUCKET
from service.site_scraper import SiteScraper
from service.util.csv_util import is_filtered, get_site_file_name
from service.util.logger_util import get_logger
from service.util.path_util import PROJECT_ROOT
from service.util.s3_util import S3Util

logger = get_logger()


class DeltaChecker:

    @staticmethod
    def get_site_deltas(site: SiteScraper, csv_path=None) -> tuple:
        # today_str = datetime.now().strftime('%Y%m%d')
        filename = get_site_file_name(site.name, True)

        previous_articles = {}

        if APP_ENV == "uat":
            s3_util = S3Util(S3_BUCKET, S3_PREFIX)
            s3_key = f"{S3_PREFIX}/{filename}"
            rows = s3_util.read_csv(s3_key)
            for row in rows:
                previous_articles[row["url"]] = row
            logger.info(f"{site.name} - previous articles: {len(previous_articles)}")
        else:
            if csv_path is None:
                csv_path = Path(PROJECT_ROOT) / S3_PREFIX / filename
            if csv_path.exists():
                with open(csv_path, encoding="utf-8", newline="") as f:
                    reader: csv.DictReader = csv.DictReader(f)
                    for row in reader:
                        row["timestamp"] = datetime.fromisoformat(row["timestamp"])
                        previous_articles[row["url"]] = row

        current_articles = {
            article.url: article
            for article in site.articles if
            not is_filtered(article, site.filter_place_keys) and not DeltaChecker.is_foreign_article(article, site.name)
        }

        new, updated, removed = [], [], []

        def timestamps_equal(t1, t2):
            return t1.replace(microsecond=0, tzinfo=None) == t2.replace(microsecond=0, tzinfo=None)

        for url, article in current_articles.items():
            if url not in previous_articles:
                new.append(article)
            else:
                prev = previous_articles[url]
                if prev["title"] != article.title or not timestamps_equal(prev["timestamp"], article.timestamp):
                    updated.append(article)

        for url in previous_articles:
            if url not in current_articles:
                removed.append(previous_articles[url])

        return previous_articles, {"new": new, "updated": updated, "removed": removed}

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
