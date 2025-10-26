import unittest
from unittest.mock import MagicMock

from service.util.delta_checker import DeltaChecker


class TestDeltaChecker(unittest.TestCase):

    def test_has_delta_new_article(self):
        site = MagicMock()
        site.name = "testsite"
        site.articles = [MagicMock(timestamp="2025-10-26T10:00:00", url="https://x.com/new", title="New Title")]
        # Simulate no CSV file
        result = DeltaChecker.has_delta(site)
        self.assertTrue(result)

    def test_any_site_has_delta(self):
        site1 = MagicMock()
        site1.name = "site1"
        site1.articles = [MagicMock(timestamp="2025-10-26T10:00:00", url="https://x.com/new", title="New Title")]

        site2 = MagicMock()
        site2.name = "site2"
        site2.articles = []

        result = DeltaChecker.any_site_has_delta([site1, site2])
        self.assertTrue(result)
