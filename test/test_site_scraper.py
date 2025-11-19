import unittest
from datetime import datetime
from pathlib import Path

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
            timestamp=datetime.utcnow(),
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
            timestamp=datetime.utcnow(),
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
            timestamp=datetime.utcnow(),
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


if __name__ == "__main__":
    unittest.main()
