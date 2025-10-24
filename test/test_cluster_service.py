import unittest
from datetime import datetime
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


if __name__ == "__main__":
    unittest.main()
