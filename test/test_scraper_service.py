import unittest
from unittest.mock import patch, MagicMock

from service.scraper_service import ScraperService


class TestScraperService(unittest.TestCase):
    @patch("threading.Thread")
    def test_scrape_sites_async(self, mock_thread_cls):
        mock_thread = MagicMock()
        mock_thread_cls.return_value = mock_thread

        thread = ScraperService.scrape_sites_async()

        mock_thread_cls.assert_called_once()
        mock_thread.start.assert_called_once()
        self.assertEqual(thread, mock_thread)


if __name__ == "__main__":
    unittest.main()
