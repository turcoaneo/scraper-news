import unittest
from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app


class TestClusterRoutes(unittest.TestCase):

    def setUp(self):
        self.client = TestClient(app)

    @patch("service.cluster_service.ClusterService.cluster_news")
    def test_cluster_news(self, mock_cluster_news):
        mock_cluster_news.return_value = [{"title": "Mocked Cluster"}]

        response = self.client.get("/cluster")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)
        mock_cluster_news.assert_called_once()

    @patch("service.cluster_service.ClusterService.delete_old_csvs")
    def test_delete_old_csvs(self, mock_delete_csvs):
        mock_delete_csvs.return_value = ["mocked_file.csv"]

        response = self.client.delete("/delete-old-csvs")
        self.assertEqual(response.status_code, 200)
        self.assertIn("deleted_files", response.json())
        self.assertEqual(response.json()["deleted_files"], ["mocked_file.csv"])
        mock_delete_csvs.assert_called_once()

    @patch("service.scraper_service.ScraperService.scrape_sites_async")
    def test_scrape_sites_async(self, mock_scrape):
        response = self.client.post("/scrape-sites")
        self.assertEqual(response.status_code, 200)
        self.assertIn("Scraping started", response.json()["status"])
        mock_scrape.assert_called_once()


if __name__ == "__main__":
    unittest.main()
