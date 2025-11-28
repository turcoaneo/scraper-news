import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path
from unittest.mock import patch, MagicMock

from model.article import Article
from model.model_type import ModelType
from service.site_scraper import SiteScraper


class TestSiteScraper(unittest.TestCase):

    def setUp(self):
        self.scraper = SiteScraper(
            name="test_site",
            base_url="https://example.com",
            traffic=1000,
            time_selector=".time",
            block_selector=".article",
            link_selector="a",
            title_strategy="text",
            model=ModelType.BERT
        )

    def test_site_file_path(self):
        path = self.scraper.site_file_path()
        self.assertIsInstance(path, Path)
        self.assertTrue(str(path).endswith(".csv"))
        self.assertIn("test_site", str(path))

    def test_compute_weight(self):
        self.scraper.compute_weight(total_traffic=5000)
        self.assertAlmostEqual(self.scraper.weight, 0.2)

    def test_short_print(self):
        article = Article(
            site="test_site",
            timestamp=datetime.now(timezone.utc),  # ✅ fixed utcnow
            title="Test Title",
            entities="Entity1, Entity2",
            keywords=["keyword1", "keyword2", "keyword3"],
            summary="This is a test summary for the article.",
            url="https://example.com/article",
            comments=5
        )
        self.scraper.articles.add(article)
        # Just ensure it runs without error
        self.scraper.short_print()

    def test_save_to_csv_creates_file(self):
        article = Article(
            site="test_site",
            timestamp=datetime.now(timezone.utc),  # ✅ fixed utcnow
            title="Test Title",
            entities="Entity1, Entity2",
            keywords=["keyword1", "keyword2"],
            summary="Summary text",
            url="https://example.com/article",
            comments=0
        )
        self.scraper.articles.add(article)
        path = self.scraper.site_file_path(False)
        self.scraper.save_to_csv()
        self.assertTrue(path.exists())
        path.unlink()  # Clean up

    @unittest.skip("Terminal caching issue, works by class in terminal, not when all are running")
    def test_is_filtered_exclusion(self):
        article = Article(
            site="test_site",
            timestamp=datetime.now(timezone.utc),  # ✅ fixed utcnow
            title="Becali scandal",
            entities="",
            keywords=["football"],
            summary="Becali made a statement",
            url="https://example.com/article",
            comments=0
        )
        self.assertTrue(self.scraper.filter_place_keys)
        self.assertTrue(self.scraper.filter_place_keys["excluding"])
        from service.util.csv_util import is_filtered
        self.assertTrue(is_filtered(article, self.scraper.filter_place_keys))

    # 🔎 New tests for scrape_recent_articles

    @patch("service.site_scraper.requests.get")
    def test_scrape_recent_articles_deduplicate(self, mock_get):
        # Fake homepage with duplicate links
        html = """
        <div class="article"><a href="/article1">Title1</a></div>
        <div class="article"><a href="/article1">Title1 duplicate</a></div>
        """
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = html

        # Patch ArticleScraper to avoid real HTTP
        with patch("service.site_scraper.ArticleScraper") as mock_scraper_cls:
            mock_scraper = MagicMock()
            mock_scraper.extract_data.return_value = {
                "timestamp": datetime.now(timezone.utc),
                "title": "Test Title",
                "entities": [],
                "keywords": [],
                "summary": "Summary",
                "url": "https://example.com/article1",
                "comments": 0,
            }
            mock_scraper_cls.return_value = mock_scraper

            self.scraper.scrape_recent_articles(minutes=180)
            # Only one article should be added despite duplicate links
            self.assertEqual(len(self.scraper.articles), 1)

    @patch("service.site_scraper.requests.get")
    def test_scrape_recent_articles_filters_by_cutoff(self, mock_get):
        html = '<div class="article"><a href="/article2">Title2</a></div>'
        mock_get.return_value.status_code = 200
        mock_get.return_value.text = html

        with patch("service.site_scraper.ArticleScraper") as mock_scraper_cls:
            mock_scraper = MagicMock()
            # Article older than cutoff
            mock_scraper.extract_data.return_value = {
                "timestamp": datetime.now(timezone.utc) - timedelta(days=1),
                "title": "Old Title",
                "entities": [],
                "keywords": [],
                "summary": "Old Summary",
                "url": "https://example.com/article2",
                "comments": 0,
            }
            mock_scraper_cls.return_value = mock_scraper

            self.scraper.scrape_recent_articles(minutes=60)
            # Should not add because it's older than cutoff
            self.assertEqual(len(self.scraper.articles), 0)


if __name__ == "__main__":
    unittest.main()
