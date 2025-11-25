import unittest
from datetime import datetime
from unittest.mock import MagicMock
from service.util.scrape_runner_merge_util import ScrapeRunnerMergeUtil


class TestScrapeRunnerMergeUtil(unittest.TestCase):

    def test_process_merge_phase(self):
        site = MagicMock()
        site.name = "site"
        site_deltas = {
            "site": (
                {"http://a": {"timestamp": datetime.now(), "title": "t", "url": "http://a"}},
                {"removed": [], "updated": [], "new": []},
            )
        }
        ScrapeRunnerMergeUtil.process_merge_phase([site], site_deltas)
        self.assertTrue(hasattr(site, "articles"))
