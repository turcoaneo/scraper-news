import unittest
from unittest.mock import MagicMock, patch

from service.article_scraper import ArticleScraper


class TestArticleExtractor(unittest.TestCase):
    def setUp(self):
        patcher = patch("service.article_scraper.extract_named_entities", return_value=["Entity1", "Entity2"])
        self.mock_entities = patcher.start()
        self.addCleanup(patcher.stop)

        self.extractor = ArticleScraper("", "", "")
        self.extractor.valid = True
        self.extractor.soup = True
        self.extractor.site_name = "testsite"
        self.extractor.time_selector = "time"
        self.extractor.homepage_url = "https://example.com/article"

        # Mock methods
        self.extractor.extract_title = MagicMock(return_value="Test Title")
        self.extractor.extract_timestamp_from_selector = MagicMock(return_value="2025-09-02T12:00:00+00:00")
        self.extractor._extract_summary = MagicMock(return_value="This is a test summary.")
        self.extractor._extract_comments = MagicMock(return_value=5)
        self.extractor.extract_keywords_from_summary = MagicMock(return_value=["test", "summary"])

    def test_extract_data_returns_expected_dict(self):
        expected = {
            "title": "Test Title",
            "timestamp": "2025-09-02T12:00:00+00:00",
            "entities": "Entity1, Entity2",
            "keywords": "test, summary",
            "summary": "This is a test summary.",
            "url": "https://example.com/article",
            "comments": "5"
        }
        result = self.extractor.extract_data()
        self.assertEqual(result, expected)

    def test_extract_data_returns_none_if_invalid(self):
        self.extractor.valid = False
        result = self.extractor.extract_data()
        self.assertIsNone(result)

    def test_extract_data_returns_none_if_no_soup(self):
        self.extractor.soup = False
        result = self.extractor.extract_data()
        self.assertIsNone(result)
