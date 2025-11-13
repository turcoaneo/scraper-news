import os

import requests
from bs4 import BeautifulSoup

from app.utils.env_vars import APP_ENV
from model.model_type import ModelType
from service.util import article_timestamp_util as ts_util
from service.util.csv_util import fix_romanian_diacritics
from service.util.entity_extraction_facade import EntityExtractorFacade
from service.util.path_util import PROJECT_ROOT

BASE_DIR = PROJECT_ROOT
EXAMPLE_PATH = os.path.join(BASE_DIR, "storage", "training", "example.json")


class ArticleScraper:
    def __init__(self, homepage_url, homepage_title, time_selector, path: str = None):
        self.homepage_url = homepage_url
        self.homepage_title = homepage_title
        self.time_selector = time_selector
        self.soup = None
        self.valid = False
        if path is None and APP_ENV == "local" or APP_ENV == "test":
            from service.claude_prompt_builder import load_training_data
            self.training_data = load_training_data(EXAMPLE_PATH)

    def fetch(self):
        try:
            response = self._request_homepage()
            if response.status_code == 200:
                self.soup = BeautifulSoup(response.text, "html.parser")
                self.valid = self.validate_article()
            else:
                print("Error, response code: " + str(response.status_code) + " for " + self.homepage_title)
                self.valid = False
        except Exception as e:
            print("Error fetching" + self.homepage_title + ": " + str(e))
            self.valid = False

    def validate_article(self):
        page_title_tag = self._extract_title()
        if not page_title_tag:
            return False

        page_title = page_title_tag.get_text(strip=True).lower()
        homepage_title = self.homepage_title.lower()

        return homepage_title[:30] in page_title or page_title[:30] in homepage_title

    def extract_data(self, model_type: ModelType = ModelType.BERT):
        if not self.valid or not self.soup:
            return None

        summary = self._extract_summary()
        result = {
            "entities": [],
            "keywords": []
        }
        try:
            if APP_ENV == "local" or APP_ENV == "test":
                result = EntityExtractorFacade.extract_by_model(summary, model_type, self.training_data)
            else:
                result = EntityExtractorFacade.get_bert_extractor_cached().extract_with_roberta(summary)
        except Exception as e:
            print("EntityExtractorFacade error" + self.homepage_title + ": " + str(e))

        return {
            "title": str(self.extract_title()),
            "timestamp": self.extract_timestamp_from_selector(self.time_selector),
            "entities": ", ".join(result["entities"]),
            "keywords": ", ".join(result["keywords"]),
            "summary": str(summary),
            "url": str(self.homepage_url),
            "comments": str(self._extract_comments())
        }

    def extract_title(self, unwanted_tags=None):
        if unwanted_tags is None:
            unwanted_tags = ["Exclusiv", "UPDATE", "Oficial", "FOTO", "VIDEO", "FOTO ȘI VIDEO", "EXCLUSIV / UPDATE"]

        tag = self._extract_title()
        if not tag:
            return ""

        # Remove span tags with known classes
        for span in tag.find_all("span", class_=["tag", "marcaj"]):
            span.extract()

        title = tag.get_text(strip=True)

        # Remove unwanted phrases from the beginning of the title
        for phrase in unwanted_tags:
            if title.upper().startswith(phrase.upper()):
                title = title[len(phrase):].strip(" :–-")

        return title

    def extract_title_naive(self):
        tag = self._extract_title()
        return tag.get_text(strip=True) if tag else ""

    def extract_timestamp_from_selector(self, selector, return_both: bool = False):
        return ts_util.extract_timestamp_from_selector(self.soup, selector, return_both)

    def _request_homepage(self):
        return requests.get(self.homepage_url, headers={"User-Agent": "Mozilla/5.0"})

    def _extract_title(self):
        return self.soup.find("h1")

    def _extract_summary(self):
        meta_desc = self.soup.find("meta", {"name": "description"})
        if meta_desc and meta_desc.has_attr("content"):
            return fix_romanian_diacritics(meta_desc["content"])

        p_tag = self.soup.find("p")
        summary = p_tag.get_text(strip=True) if p_tag else ""
        return fix_romanian_diacritics(summary)

    def _extract_comments(self):
        comment_tag = self.soup.find("div", class_="comments-no")
        if comment_tag:
            try:
                return int(comment_tag.get_text(strip=True))
            except Exception:
                pass
        return 0
