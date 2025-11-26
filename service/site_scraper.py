import csv
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Literal, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from app.utils.env_vars import APP_ENV
from model.article import Article
from model.model_type import ModelType
from service.article_scraper import ArticleScraper
from service.util.csv_util import save_articles_to_csv, get_site_file_name
from service.util.logger_util import get_logger
from service.util.path_util import PROJECT_ROOT

logger = get_logger()


def sanitize_quotes(text):
    return text.replace("„", '"').replace("”", '"') if text else text


class SiteScraper:
    title_strategy: Literal["text", "attribute"]
    title_attribute: Optional[str] = None  # e.g., "title"
    file_base: Path = os.path.abspath(os.path.join(PROJECT_ROOT, "storage"))

    def __init__(self, name, base_url, traffic, time_selector, block_selector, link_selector, title_strategy,
                 title_attribute=None, weight=0.0, filter_place_keys=None, model: ModelType = ModelType.BERT):
        self.name = name
        self.base_url = base_url
        self.traffic = traffic
        self.weight = weight
        self.articles = set()
        self.time_selector = time_selector
        self.block_selector = block_selector
        self.link_selector = link_selector
        self.title_strategy = title_strategy
        self.title_attribute = title_attribute
        self.model_type = model

        if filter_place_keys is None:
            from app.utils.env_vars import FILTER_PLACE_KEYS
            self.filter_place_keys = FILTER_PLACE_KEYS
        else:
            self.filter_place_keys = filter_place_keys

    def compute_weight(self, total_traffic):
        self.weight = self.traffic / total_traffic

    def short_print(self):
        print(f"\n📡 Site: {self.name} — {len(self.articles)} articles\n" + "-" * 60)
        for article in self.articles:
            title = getattr(article, "title", "")
            keywords = ", ".join(getattr(article, "keywords", [])[:3])
            summary_words = " ".join(getattr(article, "summary", "").split()[:20])
            timestamp = getattr(article, "timestamp")
            readable_time = timestamp.strftime("%Y-%m-%d %H:%M:%S %Z") if timestamp else "N/A"

            print(f"📰 {title}")
            print(f"🔑 Keywords: {keywords}")
            print(f"📄 Summary: {summary_words}...")
            print(f"🕒 Published: {readable_time}")
            print("-" * 60)

    def site_file_path(self, use_temp=True) -> Path:
        # filename = f"{self.name}_{datetime.now().strftime('%Y%m%d')}.csv"
        filename = get_site_file_name(self.name, use_temp=use_temp)
        return Path(self.file_base).joinpath(filename)

    def save_to_csv(self, use_temp: bool = False):
        save_articles_to_csv(
            site_name=self.name,
            base_url=self.base_url,
            articles=self.articles,
            filter_keys=self.filter_place_keys,
            base_path=self.file_base,
            use_temp=use_temp
        )

    # noinspection PyTypeChecker
    def load_recent_from_csv(self, minutes=180, filename_override=None):
        if APP_ENV == 'uat':
            return
        filename = filename_override or self.site_file_path()
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)

        try:
            with open(filename, mode="r", encoding="utf-8", newline="") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    try:
                        timestamp = datetime.fromisoformat(row["timestamp"])
                        if timestamp.tzinfo is None:
                            timestamp = timestamp.replace(tzinfo=timezone.utc)

                        if timestamp >= cutoff:
                            article = Article(
                                site=row["site"],
                                timestamp=timestamp,
                                title=sanitize_quotes(row["title"]),
                                entities=sanitize_quotes(row["entities"]),
                                # keywords=row["keywords"].split(","),
                                keywords=[k.strip() for k in sanitize_quotes(row["keywords"]).split(",")],
                                summary=sanitize_quotes(row["summary"]),
                                url=row["url"],
                                comments=int(row["comments"])
                            )
                            self.articles.add(article)
                    except Exception as e:
                        print(e)
                        continue
        except FileNotFoundError:
            print(f"CSV file not found: {filename}")

    def fetch_homepage(self):
        response = requests.get(self.base_url, headers={"User-Agent": "Mozilla/5.0"})
        response.raise_for_status()
        return BeautifulSoup(response.text, "html.parser")

    def extract_article_links(self, soup):
        seen = set()
        for block in soup.select(self.block_selector):
            link_tag = block.select_one(self.link_selector)
            if not link_tag or not link_tag.has_attr("href"):
                continue
            full_url = urljoin(self.base_url, link_tag["href"]) if not link_tag["href"].startswith("http") else \
                link_tag["href"]
            if full_url in seen:
                continue
            seen.add(full_url)
            yield full_url, link_tag

    def scrape_recent_articles(self, minutes=180):
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)
        soup = self.fetch_homepage()
        for full_url, link_tag in self.extract_article_links(soup):
            homepage_title = (
                link_tag.get_text(strip=True)
                if self.title_strategy == "text"
                else link_tag.get(self.title_attribute, "").strip()
            )
            article_scraper = ArticleScraper(full_url, homepage_title, self.time_selector)
            article_scraper.fetch()
            article_data = article_scraper.extract_data(self.model_type)
            if article_data and article_data["timestamp"] >= cutoff:
                self.articles.add(Article(self.name, **article_data))
