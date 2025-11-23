import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

from main import app


class TestClusterRoutes(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)

    @patch("service.cluster_buffer_service.ClusterBufferService.get_cached_clusters")
    def test_cluster_cached_news(self, mock_cached):
        mock_cached.return_value = {"cached": True}
        response = self.client.get("/cluster-cached")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"cached": True})
        mock_cached.assert_called_once()

    @patch("service.cluster_buffer_service.ClusterBufferService.get_cached_filtered_clusters")
    def test_cluster_cached_filtered_news(self, mock_filtered):
        mock_filtered.return_value = {"filtered": True}
        response = self.client.post("/cluster-cached-filtered", json={"include": [], "exclude": []})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"filtered": True})
        mock_filtered.assert_called_once()

    @patch("builtins.open", side_effect=FileNotFoundError("mocked missing file"))
    def test_sites_endpoint_file_missing(self, mock_open):
        response = self.client.get("/sites")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])  # fallback branch
        mock_open.assert_called_once()

    @patch("app.routes.cluster.PROJECT_ROOT", new_callable=lambda: Path("/nonexistent"))
    def test_sites_endpoint_invalid_path(self, mock_project_root):
        response = self.client.get("/sites")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_sites_endpoint_display_names(self):
        response = self.client.get("/sites")
        self.assertEqual(response.status_code, 200)
        sites = response.json()
        self.assertEqual(sites, ["GSP", "Digisport", "Fanatik", "Prosport"])

    @patch("json.load", side_effect=ValueError("mocked invalid JSON"))
    def test_sites_endpoint_invalid_json(self, mock_json_load):
        response = self.client.get("/sites")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), [])

    def test_health_check(self):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})


if __name__ == "__main__":
    unittest.main()
