import json
import unittest
from pathlib import Path
from unittest.mock import patch, mock_open

from service.cluster_buffer_service import ClusterBufferService  # adjust path as needed


class TestClusterBufferService(unittest.TestCase):

    @patch("service.cluster_buffer_service.ClusterBufferService._get_buffer_path")
    def test_get_cached_clusters_success(self, mock_get_path):
        mock_path = Path("mock_buffer.json")
        mock_get_path.return_value = mock_path

        mock_data = {
            "timestamp": "2025-10-24T12:00:00",
            "clusters": [{"id": 1, "title": "Mock"}]
        }

        with patch("pathlib.Path.exists", return_value=True), \
                patch("builtins.open", mock_open(read_data=json.dumps(mock_data))):
            result = ClusterBufferService.get_cached_clusters()
            self.assertIn("timestamp", result)
            self.assertEqual(result["clusters"][0]["title"], "Mock")

    @patch("service.cluster_buffer_service.ClusterBufferService._get_buffer_path")
    def test_get_cached_clusters_missing_file(self, mock_get_path):
        mock_path = Path("nonexistent.json")
        mock_get_path.return_value = mock_path

        with patch("pathlib.Path.exists", return_value=False):
            result = ClusterBufferService.get_cached_clusters()
            self.assertIn("error", result)
            self.assertEqual(result["error"], "Buffer not available or malformed")
