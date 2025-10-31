import unittest
from datetime import datetime
from unittest.mock import patch, mock_open

from model.article import Article
from service.site_scraper import SiteScraper
from service.util.delta_checker import DeltaChecker


class TestDeltaCheckerWithMocks(unittest.TestCase):

    def setUp(self):
        self.site = SiteScraper("example", "https://example.com", 100, "", "", "", "text")
        self.site.filter_place_keys = dict()

        self.old_csv = [
            {
                "timestamp": "2025-10-26T10:00:00",
                "url": "https://example.com/a1",
                "title": "Old Title A"
            },
            {
                "timestamp": "2025-10-26T10:05:00",
                "url": "https://example.com/a2",
                "title": "Old Title B"
            }
        ]

    def mock_csv(self):
        output = "timestamp,url,title\n"
        for row in self.old_csv:
            output += f"{row['timestamp']},{row['url']},{row['title']}\n"
        return output

    @patch("service.util.delta_checker.Path.exists", return_value=True)
    def test_detect_new_article(self, mock_exists):
        new_article = Article(
            site="example",
            timestamp=datetime.fromisoformat("2025-10-26T10:10:00"),
            title="New Title C",
            url="https://example.com/a3",
            entities="", keywords="", summary="", comments=0
        )
        self.site.articles = [new_article]

        m = mock_open(read_data=self.mock_csv())
        with patch("builtins.open", m):
            result = DeltaChecker.get_site_deltas(self.site)
            self.assertEqual(len(result[1]["new"]), 1)
            self.assertEqual(result[1]["new"][0].url, new_article.url)
            self.assertEqual(len(result[1]["updated"]), 0)
            self.assertEqual(len(result[1]["removed"]), 2)

    @patch("service.util.delta_checker.Path.exists", return_value=True)
    def test_detect_updated_article(self, mock_exists):
        updated_article = Article(
            site="example",
            timestamp=datetime.fromisoformat("2025-10-26T10:00:00"),
            title="Updated Title A",
            url="https://example.com/a1",
            entities="", keywords="", summary="", comments=0
        )
        self.site.articles = [updated_article]

        m = mock_open(read_data=self.mock_csv())
        with patch("builtins.open", m):
            result = DeltaChecker.get_site_deltas(self.site)
            self.assertEqual(len(result[1]["updated"]), 1)
            self.assertEqual(result[1]["updated"][0].url, updated_article.url)
            self.assertEqual(len(result[1]["new"]), 0)
            self.assertEqual(len(result[1]["removed"]), 1)

    @patch("service.util.delta_checker.Path.exists", return_value=True)
    def test_detect_removed_article(self, mock_exists):
        # No articles match old CSV
        self.site.articles = []

        m = mock_open(read_data=self.mock_csv())
        with patch("builtins.open", m):
            result = DeltaChecker.get_site_deltas(self.site)
            self.assertEqual(len(result[1]["removed"]), 2)
            self.assertEqual(len(result[1]["new"]), 0)
            self.assertEqual(len(result[1]["updated"]), 0)

    @patch("service.util.delta_checker.Path.exists", return_value=True)
    def test_no_delta_exact_match(self, mock_exists):
        exact_article = Article(
            site="example",
            timestamp=datetime.fromisoformat("2025-10-26T10:00:00"),
            title="Old Title A",
            url="https://example.com/a1",
            entities="", keywords="", summary="", comments=0
        )
        self.site.articles = [exact_article]

        m = mock_open(read_data=self.mock_csv())
        with patch("builtins.open", m):
            result = DeltaChecker.get_site_deltas(self.site)
            self.assertEqual(len(result[1]["new"]), 0)
            self.assertEqual(len(result[1]["updated"]), 0)
            self.assertEqual(len(result[1]["removed"]), 1)
