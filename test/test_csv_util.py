import shutil
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

import service.util.csv_util
from service.util.csv_util import get_site_file_name, save_articles_to_csv, fix_romanian_diacritics


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
                entities=["Entity1"],
                keywords="Keyword1",
                summary="Summary text",
                url="https://testsite.com/article/1",
                comments="No comments"
            )
        }

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_get_site_file_name(self):
        path_normal = get_site_file_name(self.site_name, use_temp=False)
        path_temp = get_site_file_name(self.site_name, use_temp=True)

        self.assertTrue(path_normal.endswith(f"{self.site_name}.csv"))
        self.assertTrue(path_temp.endswith(f"{self.site_name}_buffer.csv"))

    def test_save_articles_to_csv_atomic(self):
        self.save_csv(use_temp=True)
        self.assert_path()

    def test_save_articles_to_csv_final(self):
        temp_false = False
        self.save_csv(use_temp=temp_false)
        self.assert_path(use_temp=temp_false)

    def save_csv(self, use_temp=True):
        save_articles_to_csv(
            site_name=self.site_name,
            base_url=self.base_url,
            articles=self.articles,
            filter_keys=self.filter_keys,
            base_path=self.temp_dir,
            use_temp=use_temp
        )

    def assert_path(self, use_temp=True):
        final_path = Path(self.temp_dir) / get_site_file_name(self.site_name, use_temp=use_temp)
        self.assertTrue(final_path.exists())
        with open(final_path, encoding="utf-8") as f:
            content = f.read()
            self.assertIn("Test Title", content)
            self.assertIn("Entity1", content)

    def test_fix_lowercase_diacritics(self):
        input_text = "şcoală şi ţară"
        expected = "școală și țară"
        self.assertEqual(fix_romanian_diacritics(input_text), expected)

    def test_fix_uppercase_diacritics(self):
        input_text = "Ştefan Ţiriac"
        expected = "Ștefan Țiriac"
        self.assertEqual(fix_romanian_diacritics(input_text), expected)

    def test_mixed_case_and_context(self):
        input_text = "Ştirile din ţară sunt importante"
        expected = "Știrile din țară sunt importante"
        self.assertEqual(fix_romanian_diacritics(input_text), expected)

    def test_no_diacritics(self):
        input_text = "Mureșan și Pașcanu"
        expected = "Mureșan și Pașcanu"
        self.assertEqual(fix_romanian_diacritics(input_text), expected)

    def test_edge_case_empty_string(self):
        self.assertEqual(fix_romanian_diacritics(""), "")


if __name__ == "__main__":
    unittest.main()
