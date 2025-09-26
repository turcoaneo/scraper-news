import csv
import os
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

from model.article import Article
from service.article_scraper import ArticleScraper
from service.claude_prompt_builder import load_training_data


def sanitize_quotes(text):
    return text.replace("„", '"').replace("”", '"') if text else text


def is_filtered(article, filter_place_keys):
    including = set(word.lower() for word in filter_place_keys.get("including", []))
    excluding = set(word.lower() for word in filter_place_keys.get("excluding", []))
    places = filter_place_keys.get("place", [])

    # Gather text from specified places
    text_blob = []
    for place in places:
        value = getattr(article, place, "")
        if isinstance(value, list):
            text_blob.extend(value)
        elif isinstance(value, str):
            text_blob.append(value)

    combined_text = " ".join(text_blob).lower()

    # Exclude if any exclusion keyword is found
    if any(word in combined_text for word in excluding):
        return True

    # Include only if at least one inclusion keyword is found
    if including and not any(word in combined_text for word in including):
        return True

    return False


class SiteScraper:
    title_strategy: Literal["text", "attribute"]
    title_attribute: Optional[str] = None  # e.g., "title"
    file_base: str = "storage"

    def __init__(self, name, base_url, traffic, time_selector, block_selector, link_selector, title_strategy,
                 title_attribute=None, weight=0.0, filter_place_keys=None, claude=True):
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
        self.claude = claude

        if filter_place_keys is None:
            self.filter_place_keys = {
                "place": ["url", "summary", "keywords", "title"],
                "including": [],
                "excluding": ["video", "Becali"],
            }
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

    def save_to_csv(self):
        if not os.path.exists(self.file_base):
            try:
                os.makedirs(self.file_base)
            except FileExistsError:
                # directory already exists
                pass
        filename = f"{self.file_base}/{self.name}_{datetime.now().strftime('%Y%m%d')}.csv"
        with open(filename, mode="w", encoding="utf-8", newline="") as file:
            columns = [
                "site", "timestamp", "title", "entities", "keywords", "summary", "url", "comments"
            ]
            writer = csv.DictWriter(file, fieldnames=columns, quoting=csv.QUOTE_ALL)

            writer.writeheader()
            for article in self.articles:
                # Skip external links
                if self.base_url not in article.url or is_filtered(article, self.filter_place_keys):
                    continue
                title = article.title
                writer.writerow({
                    "site": article.site,
                    "timestamp": article.timestamp.isoformat(),
                    "title": title,
                    "entities": article.entities,
                    "keywords": article.keywords,
                    "summary": article.summary,
                    "url": article.url,
                    "comments": article.comments
                })

    # noinspection PyTypeChecker
    def load_recent_from_csv(self, minutes=180, filename_override=None):
        filename = filename_override or f"{self.file_base}/{self.name}_{datetime.now().strftime('%Y%m%d')}.csv"
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)

        try:
            with open(filename, mode="r", encoding="utf-8") as file:
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

    def scrape_recent_articles(self, minutes=180):
        from datetime import timezone
        cutoff = datetime.now(timezone.utc) - timedelta(minutes=minutes)

        response = requests.get(self.base_url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(response.text, "html.parser")

        for block in soup.select(self.block_selector):
            try:
                link_tag = block.select_one(self.link_selector)
                if not link_tag or not link_tag.has_attr("href"):
                    continue

                relative_url = link_tag["href"]
                if not relative_url.startswith("http"):
                    full_url = urljoin(self.base_url, relative_url)
                else:
                    full_url = relative_url

                if self.title_strategy == "text":
                    homepage_title = link_tag.get_text(strip=True)
                elif self.title_strategy == "attribute" and self.title_attribute:
                    homepage_title = link_tag.get(self.title_attribute, "").strip()
                else:
                    continue

                article_scraper = ArticleScraper(full_url, homepage_title, self.time_selector)
                article_scraper.fetch()
                article_data = article_scraper.extract_data(self.claude)

                if article_data and article_data["timestamp"] >= cutoff:
                    self.articles.add(Article(self.name, article_data["timestamp"], article_data["title"],
                                              article_data["entities"], article_data["keywords"],
                                              article_data["summary"], article_data["url"], article_data["comments"]))

            except Exception as ex:
                print("Failing scraping recent articles - ", ex)
                continue
