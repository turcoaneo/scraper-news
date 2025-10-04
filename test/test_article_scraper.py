import unittest
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

from bs4 import BeautifulSoup

from model.model_type import ModelType
from service.article_scraper import ArticleScraper


class TestArticleScraper(unittest.TestCase):
    def setUp(self):
        self.scraper = ArticleScraper(
            homepage_url="https://example.com/article",
            homepage_title="Rapid București câștigă dramatic",
            time_selector="time"
        )
        self.scraper.valid = True
        self.scraper.soup = MagicMock()

    @patch("service.article_scraper.ArticleScraper._extract_title")
    def test_validate_article_true(self, mock_title):
        mock_tag = MagicMock()
        mock_tag.get_text.return_value = "Rapid București câștigă dramatic"
        mock_title.return_value = mock_tag
        self.assertTrue(self.scraper.validate_article())

    @patch("service.article_scraper.ArticleScraper._extract_title")
    def test_validate_article_false(self, mock_title):
        mock_tag = MagicMock()
        mock_tag.get_text.return_value = "Alt titlu complet diferit"
        mock_title.return_value = mock_tag
        self.assertFalse(self.scraper.validate_article())

    @patch("service.article_scraper.EntityExtractorFacade.extract_by_model")
    @patch("service.article_scraper.ArticleScraper._extract_summary", return_value="Rezumat test")
    @patch("service.article_scraper.ArticleScraper._extract_comments", return_value=3)
    def test_extract_data(self, mock_summary, mock_comments, mock_extract):  # reverse order for patched params
        mock_extract.return_value = {
            "entities": ["Rapid București", "CFR Cluj"],
            "keywords": ["victorie", "dramatică"]
        }
        self.scraper.extract_title = MagicMock(return_value="Rapid București câștigă dramatic")
        self.scraper.extract_timestamp_from_selector = MagicMock(
            return_value=datetime(2025, 10, 4, 12, 0, tzinfo=timezone.utc))

        result = self.scraper.extract_data(model_type=ModelType.SPACY)
        self.assertEqual(result["title"], "Rapid București câștigă dramatic")
        self.assertIn("Rapid București", result["entities"])
        self.assertIn("victorie", result["keywords"])
        self.assertEqual(result["comments"], "3")

    def test_extract_title_removes_prefix(self):
        mock_tag = MagicMock()
        mock_tag.find_all.return_value = []
        mock_tag.get_text.return_value = "FOTO Rapid București câștigă dramatic"
        self.scraper._extract_title = MagicMock(return_value=mock_tag)

        title = self.scraper.extract_title()
        self.assertEqual(title, "Rapid București câștigă dramatic")

    def test_extract_timestamp_from_selector_digisport(self):
        mock_tag = MagicMock()
        mock_tag.get_text.return_value = "19.08.2025, 16:04"
        self.scraper._extract_time_selector = MagicMock(return_value=mock_tag)

        ts = self.scraper.extract_timestamp_from_selector("time", True)
        self.assertEqual(ts[0].year, 2025)
        self.assertEqual(ts[0].month, 8)
        self.assertEqual(ts[0].hour, 16)

    def test_extract_timestamp_from_selector_gsp(self):
        mock_tag = MagicMock()
        mock_tag.get_text.return_value = "19 august 2025, 16:15"
        self.scraper._extract_time_selector = MagicMock(return_value=mock_tag)

        ts = self.scraper.extract_timestamp_from_selector("time")
        self.assertEqual(ts.year, 2025)
        self.assertEqual(ts.month, 8)
        self.assertEqual(ts.hour, 13)

    @patch("service.article_scraper.ArticleScraper._request_homepage")
    def test_fetch_success(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = "<html><h1>Rapid București câștigă dramatic</h1></html>"
        mock_request.return_value = mock_response

        with patch("service.article_scraper.ArticleScraper.validate_article", return_value=True):
            self.scraper.fetch()
            self.assertTrue(self.scraper.valid)
            self.assertIsNotNone(self.scraper.soup)

    @patch("service.article_scraper.ArticleScraper._request_homepage")
    def test_fetch_failure(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_request.return_value = mock_response

        self.scraper.fetch()
        self.assertFalse(self.scraper.valid)


if __name__ == "__main__":
    unittest.main()


    def test_digisport_title(self):
        html = '<h1><span class="tag">Exclusiv</span> Daniel Pancu nu are dubii</h1>'
        scraper = ArticleScraper("url", "title", "")
        scraper.soup = BeautifulSoup(html, "html.parser")
        self.assertEqual(scraper.extract_title_naive(), "ExclusivDaniel Pancu nu are dubii")
        self.assertEqual(scraper.extract_title(), "Daniel Pancu nu are dubii")


    def test_gsp_title_with_multiple_tags(self):
        html = '''
        <h1>
            <span class="marcaj ">FOTO ȘI VIDEO EXCLUSIV</span>
            „Colosseumul” României e gata în proporție de 70%
        </h1>
        '''
        scraper = ArticleScraper("url", "title", "")
        scraper.soup = BeautifulSoup(html, "html.parser")
        self.assertEqual(scraper.extract_title(), "„Colosseumul” României e gata în proporție de 70%")


    def test_title_without_span(self):
        html = '<h1>Un meci spectaculos în Liga 1</h1>'
        scraper = ArticleScraper("url", "title", "")
        scraper.soup = BeautifulSoup(html, "html.parser")
        self.assertEqual(scraper.extract_title_naive(), "Un meci spectaculos în Liga 1")
        self.assertEqual(scraper.extract_title(), "Un meci spectaculos în Liga 1")


    def test_custom_unwanted_tags(self):
        html = '<h1><span class="tag">Blah Blah</span> Titlu important</h1>'
        scraper = ArticleScraper("url", "title", "")
        scraper.soup = BeautifulSoup(html, "html.parser")
        self.assertEqual(scraper.extract_title(unwanted_tags=["Blah Blah"]), "Titlu important")

if __name__ == "__main__":
    unittest.main()
