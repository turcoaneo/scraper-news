import json
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock


class TestClusterService(unittest.TestCase):

    @patch("service.cluster_service.StoryClusterer")
    @patch("app.config.loader.load_sites_from_config")
    @patch("service.site_scraper.SiteScraper.load_recent_from_csv", return_value=None)
    def test_cluster_news(self, mock_load_csv, mock_loader, mock_clusterer_cls):
        from service.cluster_service import ClusterService

        mock_site = MagicMock()
        mock_site.traffic = 100
        mock_loader.return_value = [mock_site]

        mock_clusterer = MagicMock()
        mock_clusterer.get_matched_clusters.return_value = {"clusters": []}
        mock_clusterer.cluster_stories = MagicMock()
        mock_clusterer_cls.side_effect = lambda *args, **kwargs: mock_clusterer

        result = ClusterService.cluster_news()
        self.assertEqual(result, {"clusters": []})
        mock_clusterer.cluster_stories.assert_called_once()

    @patch("pathlib.Path.glob")
    @patch("app.config.loader.load_sites_from_config")
    def test_delete_old_csvs(self, mock_loader, mock_glob):
        from service.cluster_service import ClusterService

        mock_file_today = MagicMock()
        mock_file_today.name = datetime.now().strftime("%Y%m%d") + "_results.csv"

        mock_file_old = MagicMock()
        mock_file_old.name = "20251015_results.csv"

        mock_glob.return_value = [mock_file_today, mock_file_old]

        result = ClusterService.delete_old_csvs()
        self.assertEqual(result, ["20251015_results.csv"])
        mock_file_old.unlink.assert_called_once()
        mock_file_today.unlink.assert_not_called()

    @patch("service.cluster_service.ClusterService.cluster_news")
    @patch("service.cluster_service.ClusterService.get_csv_buffer_result_path")
    def test_save_cluster_buffer_success(self, mock_get_buffer_path, mock_cluster_news):
        from service.cluster_service import ClusterService
        # Setup
        mock_cluster_news.return_value = [{"id": 1, "title": "Mock Story"}]

        temp_dir = Path("test_storage")
        temp_dir.mkdir(exist_ok=True)
        buffer_path = temp_dir / "buffer.json"
        mock_get_buffer_path.return_value = buffer_path

        # Act
        result_path = ClusterService.save_cluster_buffer(sites=["site1", "site2"], minutes=60)

        # Assert
        self.assertIsNotNone(result_path)
        self.assertTrue(result_path.exists())

        with open(result_path, "r", encoding="utf-8", newline="") as f:
            data = json.load(f)
            self.assertIn("timestamp", data)
            self.assertEqual(data["clusters"], [{"id": 1, "title": "Mock Story"}])

        # Bonus Tip: Cleanup safely
        try:
            if result_path.exists():
                result_path.unlink()
            if temp_dir.exists():
                temp_dir.rmdir()
        except Exception as cleanup_error:
            print(f"Cleanup failed: {cleanup_error}")

    @patch("service.cluster_service.ClusterService.cluster_news", side_effect=Exception("Boom"))
    @patch("service.cluster_service.ClusterService.get_storage_path")
    def test_save_cluster_buffer_failure(self, mock_get_storage_path, mock_cluster_news):
        from service.cluster_service import ClusterService
        mock_get_storage_path.return_value = Path("test_storage")
        result = ClusterService.save_cluster_buffer(sites=[], minutes=10)
        self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
