import unittest
from unittest.mock import MagicMock
from urllib.parse import urljoin

from model.model_type import ModelType
from service.site_scraper import SiteScraper


class TestExtractArticleLinks(unittest.TestCase):

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

    def _make_block(self, href=None, inner_href=None):
        """Helper to create a fake block element with optional hrefs."""
        block = MagicMock()
        block.get.return_value = href
        # Simulate dict‑style access
        block.__getitem__.side_effect = (
            lambda k: {"href": href}[k] if href else None
        )

        if inner_href:
            inner_link = MagicMock()
            inner_link.has_attr.return_value = True
            inner_link.__getitem__.side_effect = (
                lambda k: {"href": inner_href}[k]
            )
            block.select_one.return_value = inner_link
        else:
            block.select_one.return_value = None

        return block

    def test_direct_href(self):
        """Block has direct href → should yield normalized full_url"""
        block = self._make_block(href="/article1")
        soup = MagicMock()
        soup.select.return_value = [block]

        results = list(self.scraper.extract_article_links(soup))
        self.assertEqual(results[0][0], urljoin(self.scraper.base_url, "/article1"))

    def test_inner_link_href(self):
        """Block has no href, but inner link has one → should yield"""
        block = self._make_block(href=None, inner_href="/article2")
        soup = MagicMock()
        soup.select.return_value = [block]

        results = list(self.scraper.extract_article_links(soup))
        self.assertEqual(results[0][0], urljoin(self.scraper.base_url, "/article2"))

    def test_skip_block_without_href(self):
        """Block has no href and no inner link → should skip"""
        block = self._make_block(href=None, inner_href=None)
        soup = MagicMock()
        soup.select.return_value = [block]

        results = list(self.scraper.extract_article_links(soup))
        self.assertEqual(results, [])

    def test_full_url_preserved(self):
        """Block href already absolute → should not prepend base_url"""
        block = self._make_block(href="https://other.com/article3")
        soup = MagicMock()
        soup.select.return_value = [block]

        results = list(self.scraper.extract_article_links(soup))
        self.assertEqual(results[0][0], "https://other.com/article3")

    def test_duplicate_links_skipped(self):
        """Duplicate hrefs → only one yielded"""
        block1 = self._make_block(href="/dup")
        block2 = self._make_block(href="/dup")
        soup = MagicMock()
        soup.select.return_value = [block1, block2]

        results = list(self.scraper.extract_article_links(soup))
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0][0], urljoin(self.scraper.base_url, "/dup"))


if __name__ == "__main__":
    unittest.main()
