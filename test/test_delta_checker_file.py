import unittest
from datetime import datetime
from pathlib import Path

from model.article import Article
from model.model_type import ModelType
from service.site_scraper import SiteScraper
from service.util.delta_checker import DeltaChecker
from service.util.path_util import PROJECT_ROOT


class TestDeltaChecker(unittest.TestCase):

    def setUp(self):
        filename = "digisport_dump.csv"
        self.csv_path = Path(PROJECT_ROOT) / "test" / "storage" / filename

        self.site = SiteScraper(
            name="digisport",
            base_url="https://www.digisport.ro",
            traffic=1000,
            time_selector=".time",
            block_selector=".article",
            link_selector="a",
            title_strategy="text",
            model=ModelType.BERT
        )
        self.site.site_file_path = lambda: self.csv_path

        # Base article from CSV
        self.base_article = Article(
            site="digisport",
            timestamp=datetime.fromisoformat("2025-10-26T06:13:00+00:00"),
            title="După ce a spus că ”Real Madrid fură și se plânge tot timpul”, Lamine Yamal a mai ”lovit” o dată",
            entities="irrelevant",
            keywords="irrelevant",
            summary="irrelevant",
            url="https://www.digisport.ro/fotbal/la-liga/dupa-ce-a-spus-ca-real-madrid-fura-si-se-plange-tot-timpul-lamine-yamal-a-mai-lovit-o-data-3885961",
            comments=0
        )

    def test_no_delta_exact_match(self):
        self.site.articles = {self.base_article}
        self.site.articles.add(
            Article(
                site="digisport",
                timestamp=datetime.fromisoformat("2025-10-26T06:21:00+00:00"),
                title="Cristi Chivu, așa cum rar a fost văzut: a început să strige în conferință și a urmat ceva complet neașteptat, după 1-3 cu Napoli",
                entities="irrelevant",
                keywords="irrelevant",
                summary="irrelevant",
                url="https://www.digisport.ro/fotbal/serie-a/cristi-chivu-asa-cum-rar-a-fost-vazut-a-inceput-sa-strige-in-conferinta-si-a-urmat-ceva-complet-neasteptat-dupa-1-3-cu-napoli-3885963",
                comments=0
            )
        )
        result = DeltaChecker.has_delta(self.site, self.csv_path)
        self.assertFalse(result)

    def test_new_article_detected(self):
        new_article = Article(
            site="digisport",
            timestamp=datetime.fromisoformat("2025-10-26T07:00:00+00:00"),
            title="New breaking news",
            entities="irrelevant",
            keywords="irrelevant",
            summary="irrelevant",
            url="https://www.digisport.ro/fotbal/la-liga/new-breaking-news-3885999",
            comments=0
        )
        self.site.articles = {self.base_article, new_article}
        result = DeltaChecker.has_delta(self.site, self.csv_path)
        self.assertTrue(result)

    def test_title_changed_detected(self):
        changed_title = Article(
            site=self.base_article.site,
            timestamp=self.base_article.timestamp,
            title="Lamine Yamal provoacă din nou",
            entities=self.base_article.entities,
            keywords=self.base_article.keywords,
            summary=self.base_article.summary,
            url=self.base_article.url,
            comments=self.base_article.comments
        )
        self.site.articles = {changed_title}
        result = DeltaChecker.has_delta(self.site, self.csv_path)
        self.assertTrue(result)

    def test_url_changed_detected(self):
        changed_url = Article(
            site=self.base_article.site,
            timestamp=self.base_article.timestamp,
            title=self.base_article.title,
            entities=self.base_article.entities,
            keywords=self.base_article.keywords,
            summary=self.base_article.summary,
            url="https://www.digisport.ro/fotbal/la-liga/lamine-yamal-provocare-noua-3885999",
            comments=self.base_article.comments
        )
        self.site.articles = {changed_url}
        result = DeltaChecker.has_delta(self.site, self.csv_path)
        self.assertTrue(result)

    def test_timestamp_changed_detected(self):
        changed_time = Article(
            site=self.base_article.site,
            timestamp=datetime.fromisoformat("2025-10-26T06:14:00+00:00"),  # 1 min later
            title=self.base_article.title,
            entities=self.base_article.entities,
            keywords=self.base_article.keywords,
            summary=self.base_article.summary,
            url=self.base_article.url,
            comments=self.base_article.comments
        )
        self.site.articles = {changed_time}
        result = DeltaChecker.has_delta(self.site, self.csv_path)
        self.assertTrue(result)
