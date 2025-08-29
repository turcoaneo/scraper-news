import unittest

from site_scraper import is_filtered


class TestArticleFilter(unittest.TestCase):

    def setUp(self):
        self.filter_config = {
            "place": ["url", "summary", "keywords", "title"],
            "including": ["tennis", "Cîrstea"],
            "excluding": ["video", "Cristi", "Chivu"]
        }

    def test_including_keyword_passes(self):
        article = {
            "url": "https://sport.ro/tennis/sorana-cirstea",
            "summary": "Sorana Cîrstea wins again",
            "keywords": ["tennis", "victory"],
            "title": "Cîrstea triumfă la US Open"
        }
        self.assertFalse(is_filtered(article, self.filter_config))

    def test_excluding_keyword_blocks(self):
        article = {
            "url": "https://sport.ro/football/cristi-chivu",
            "summary": "Cristi Chivu speaks out",
            "keywords": ["football", "interview"],
            "title": "Cristi Chivu despre Inter"
        }
        self.assertTrue(is_filtered(article, self.filter_config))

    def test_missing_including_blocks(self):
        article = {
            "url": "https://sport.ro/snooker/ronnie",
            "summary": "Ronnie O'Sullivan wins",
            "keywords": ["snooker", "champion"],
            "title": "Ronnie domină din nou"
        }
        self.assertTrue(is_filtered(article, self.filter_config))

    def test_empty_filter_passes_all(self):
        article = {
            "url": "https://sport.ro/snooker/ronnie",
            "summary": "Ronnie O'Sullivan wins",
            "keywords": ["snooker", "champion"],
            "title": "Ronnie domină din nou"
        }
        self.assertFalse(is_filtered(article, {"place": ["summary"]}))

    def test_video_url(self):
        filter_place_keys = {
            "place": ["url", "summary", "keywords", "title"],
            "including": [],
            "excluding": ["video"],
        }
        article = {
            "url": "https://www.digisport.ro/fotbal/serie-a/inter-torino-live-video-2145-digi-sport-1",
            "summary": "Cristi Chivu",
            "keywords": ["fotbal", "champion"],
            "title": "Meazza"
        }
        self.assertTrue(is_filtered(article, filter_place_keys))

    def test_video_title(self):
        filter_place_keys = {
            "place": ["title"],
            "including": [],
            "excluding": ["video"],
        }
        article = {
            "url": "https://www.digisport.ro/fotbal/serie-a/inter-torino-live-video-2145-digi-sport-1",
            "summary": "Cristi Chivu",
            "keywords": ["fotbal", "champion"],
            "title": "Video-Cristi-Chivu"
        }
        self.assertTrue(is_filtered(article, filter_place_keys))
