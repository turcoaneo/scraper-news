import re
from collections import Counter
from datetime import datetime, timezone

import requests
from bs4 import BeautifulSoup
from dateutil import parser

from named_entity import NamedEntity

stopwords = {
            "asta", "ăsta", "acesta", "această", "există", "care", "pentru", "este", "și", "din", "cu", "sunt",
            "mai", "mult", "foarte", "fie", "cum", "dar", "nu", "în", "la", "de"
        }


def extract_named_entities(summary):
    return NamedEntity().extract_ents(summary)


class ArticleScraper:
    def __init__(self, homepage_url, homepage_title, time_selector):
        self.homepage_url = homepage_url
        self.homepage_title = homepage_title
        self.time_selector = time_selector
        self.soup = None
        self.valid = False
        self.data = {}

    def extract_keywords_from_summary(self):
        summary = self._extract_summary().lower()
        words = re.findall(r'\b\w{5,}\b', summary)
        filtered_words = [word for word in words if word not in stopwords]
        word_counts = Counter(filtered_words)
        most_common = [word for word, count in word_counts.most_common(10)]
        return most_common

    def fetch(self):
        try:
            response = requests.get(self.homepage_url, headers={"User-Agent": "Mozilla/5.0"})
            if response.status_code == 200:
                self.soup = BeautifulSoup(response.text, "html.parser")
                self.valid = self.validate_article()
        except Exception:
            self.valid = False

    def validate_article(self):
        page_title_tag = self.soup.find("h1")
        if not page_title_tag:
            return False

        page_title = page_title_tag.get_text(strip=True).lower()
        homepage_title = self.homepage_title.lower()

        return homepage_title[:30] in page_title or page_title[:30] in homepage_title

    def extract(self):
        if not self.valid or not self.soup:
            return None

        summary = self._extract_summary()

        self.data["title"] = self.extract_title()
        self.data["timestamp"] = self.extract_timestamp_from_selector(self.time_selector)
        self.data["entities"] = extract_named_entities(summary)
        self.data["keywords"] = self.extract_keywords_from_summary()
        self.data["summary"] = summary
        self.data["url"] = self.homepage_url
        self.data["comments"] = self._extract_comments()

        return self.data

    def extract_title(self):
        tag = self.soup.find("h1")
        return tag.get_text(strip=True) if tag else ""

    def extract_timestamp_from_selector(self, selector):
        tag = self.soup.select_one(selector)
        if tag:
            text = tag.get_text(strip=True)

            # Match Digisport-style: 19.08.2025, 16:04
            match = re.search(r"\d{2}\.\d{2}\.\d{4},\s*\d{2}:\d{2}", text)
            if not match:
                # Match GSP-style: 19 august 2025, 16:15
                match = re.search(r"\d{2}\s+\w+\s+\d{4},\s*\d{2}:\d{2}", text)

            if match:
                try:
                    dt = parser.parse(match.group(), dayfirst=True)
                    return dt.astimezone(timezone.utc)
                except Exception:
                    pass

        # Fallback: current UTC time
        return datetime.now(timezone.utc)

    def _extract_summary(self):
        meta_desc = self.soup.find("meta", {"name": "description"})
        if meta_desc and meta_desc.has_attr("content"):
            return meta_desc["content"]

        p_tag = self.soup.find("p")
        return p_tag.get_text(strip=True) if p_tag else ""

    def _extract_keywords(self):
        paragraphs = self.soup.find_all('p')
        article_text = " ".join(p.get_text() for p in paragraphs)
        words = re.findall(r'\b\w{5,}\b', article_text.lower())
        filtered_words = [word for word in words if word not in stopwords]
        word_counts = Counter(filtered_words)
        most_common = [word for word, count in word_counts.most_common(20)]
        return most_common

    def _extract_comments(self):
        comment_tag = self.soup.find("div", class_="comments-no")
        if comment_tag:
            try:
                return int(comment_tag.get_text(strip=True))
            except Exception:
                pass
        return 0
