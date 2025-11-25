import unittest

from model.article import Article
from service.util.csv_util import is_filtered


class TestArticleFilter(unittest.TestCase):

    def setUp(self):
        self.filter_config = {
            "place": ["url", "summary", "keywords", "title"],
            "including": ["tennis", "Cîrstea"],
            "excluding": ["video", "Cristi", "Chivu"]
        }

    def test_including_keyword_passes(self):
        article = Article(
            "https://sport.ro/tennis/sorana-cirstea",
            "Sorana Cîrstea wins again",
            "Cîrstea triumfă la US Open",
            ["tennis", "victory"],
            []
        )
        self.assertFalse(is_filtered(article, self.filter_config))

    def test_excluding_keyword_blocks(self):
        article = Article(
            "https://sport.ro/football/cristi-chivu",
            "Cristi Chivu speaks out",
            "Cristi Chivu despre Inter",
            ["football", "interview"],
            []
        )
        self.assertTrue(is_filtered(article, self.filter_config))

    def test_missing_including_blocks(self):
        article = Article(
            "https://sport.ro/snooker/ronnie",
            "Ronnie O'Sullivan wins",
            "Ronnie domină din nou",
            ["snooker", "champion"],
            []
        )
        self.assertTrue(is_filtered(article, self.filter_config))

    def test_empty_filter_passes_all(self):
        article = Article(
            "https://sport.ro/snooker/ronnie",
            "Ronnie O'Sullivan wins",
            "Ronnie domină din nou",
            ["snooker", "champion"],
            []
        )
        self.assertFalse(is_filtered(article, {"place": ["summary"]}))

    def test_video_url(self):
        filter_place_keys = {
            "place": ["url", "summary", "keywords", "title"],
            "including": [],
            "excluding": ["video"],
        }
        article = Article(
            "https://www.digisport.ro/fotbal/serie-a/inter-torino-live-video-2145-digi-sport-1",
            "Cristi Chivu",
            "Video - Meazza",
            ["fotbal", "champion"],
            []
        )
        self.assertTrue(is_filtered(article, filter_place_keys))

    def test_video_title(self):
        filter_place_keys = {
            "place": ["title"],
            "including": [],
            "excluding": ["video"],
        }
        article = Article(
            "https://www.digisport.ro/fotbal/serie-a/inter-torino-live-video-2145-digi-sport-1",
            "Cristi Chivu",
            "Video-Cristi-Chivu",
            ["fotbal", "champion"],
            []
        )
        self.assertTrue(is_filtered(article, filter_place_keys))
