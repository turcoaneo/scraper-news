import shutil
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

import service.util.csv_util
from service.util.csv_util import get_site_file_path, save_articles_to_csv


class DummyArticle:
    def __init__(self, site, timestamp, title, entities, keywords, summary, url, comments):
        self.site = site
        self.timestamp = timestamp
        self.title = title
        self.entities = entities
        self.keywords = keywords
        self.summary = summary
        self.url = url
        self.comments = comments


# noinspection PyUnusedLocal
def dummy_is_filtered(article, filter_keys):
    return False  # Always include for testing


# Patch the filter function
service.util.csv_util.is_filtered = dummy_is_filtered


class TestCsvUtil(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.site_name = "TestSite"
        self.base_url = "https://testsite.com"
        self.filter_keys = {}
        self.articles = {
            DummyArticle(
                site=self.site_name,
                timestamp=datetime.now(),
                title="Test Title",
                entities="Entity1",
                keywords="Keyword1",
                summary="Summary text",
                url="https://testsite.com/article/1",
                comments="No comments"
            )
        }

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_get_site_file_path(self):
        path_normal = get_site_file_path(self.site_name, self.temp_dir, use_temp=False)
        path_temp = get_site_file_path(self.site_name, self.temp_dir, use_temp=True)

        today = datetime.now().strftime('%Y%m%d')
        self.assertTrue(str(path_normal).endswith(f"{self.site_name}_{today}.csv"))
        self.assertTrue(str(path_temp).endswith(f"{self.site_name}_{today}_buffer.csv"))

    def test_save_articles_to_csv_atomic(self):
        self.save_csv(use_temp=True)
        self.assert_path()

    def test_save_articles_to_csv_final(self):
        self.save_csv(use_temp=False)
        self.assert_path()

    def save_csv(self, use_temp=True):
        save_articles_to_csv(
            site_name=self.site_name,
            base_url=self.base_url,
            articles=self.articles,
            filter_keys=self.filter_keys,
            base_path=self.temp_dir,
            use_temp=use_temp
        )

    def assert_path(self):
        final_path = get_site_file_path(self.site_name, self.temp_dir, use_temp=False)
        self.assertTrue(final_path.exists())
        with open(final_path, encoding="utf-8") as f:
            content = f.read()
            self.assertIn("Test Title", content)
            self.assertIn("Entity1", content)


if __name__ == "__main__":
    unittest.main()
