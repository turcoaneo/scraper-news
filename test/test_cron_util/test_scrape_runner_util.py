import unittest
from unittest.mock import MagicMock, patch
from datetime import datetime, timezone, timedelta

from service.util.scrape_runner_util import ScrapeRunnerUtil
from model.article import Article


class TestScrapeRunnerUtil(unittest.TestCase):

    def test_dict_to_article(self):
        row = {
            "timestamp": datetime.now(timezone.utc),
            "title": "Test Title",
            "entities": ["entity1"],
            "keywords": ["kw1"],
            "summary": "summary",
            "url": "http://test",
            "comments": "5",
        }
        article = ScrapeRunnerUtil.dict_to_article(row, "TestSite")
        self.assertEqual(article.site, "TestSite")
        self.assertEqual(article.title, "Test Title")
        self.assertEqual(article.comments, 5)

    def test_merge_articles(self):
        prev = {"http://a": Article(site="s", timestamp=datetime.now(), title="t", url="http://a", entities=["entity1"],
                                    keywords=["kw1"], summary="")}
        deltas = {
            "removed": [{"url": "http://a"}],
            "updated": [{"url": "http://b", "title": "new"}],
            "new": [{"url": "http://c", "title": "new"}],
        }
        merged = ScrapeRunnerUtil.merge_articles(deltas, prev, "s")
        urls = {a.url if isinstance(a, Article) else a["url"] for a in merged}
        self.assertIn("http://b", urls)
        self.assertIn("http://c", urls)
        self.assertNotIn("http://a", urls)

    @patch("service.util.scrape_runner_util.get_last_scrape_times", return_value={})
    @patch("service.util.scrape_runner_util.update_scrape_time")
    def test_process_site_sets_time(self, mock_update, mock_get_last):
        site = MagicMock()
        site.name = "sport"
        site.scrape_recent_articles = MagicMock()
        ScrapeRunnerUtil.process_site(site, minutes=10)
        mock_update.assert_called_once()
        site.scrape_recent_articles.assert_called_once()
