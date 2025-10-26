import json
import unittest
from pathlib import Path
from unittest.mock import patch, mock_open

from service.util import buffer_util


class TestBufferUtil(unittest.TestCase):

    @patch("service.util.buffer_util.ClusterService.get_csv_buffer_result_path")
    def test_update_buffer_timestamp_success(self, mock_get_path):
        # Setup mock path and initial buffer content
        mock_path = Path("mock_buffer.json")
        mock_get_path.return_value = mock_path

        initial_data = {
            "timestamp": "2025-10-25T10:00:00",
            "clusters": [{"id": 1, "title": "Old"}]
        }

        # Patch open and simulate file read/write
        m = mock_open(read_data=json.dumps(initial_data))
        with patch("builtins.open", m), \
                patch("pathlib.Path.exists", return_value=True):
            buffer_util.update_buffer_timestamp()

        # Validate that json.dump was called with updated timestamp
        handle = m()
        written_data = json.loads("".join(call.args[0] for call in handle.write.call_args_list))
        self.assertIn("timestamp", written_data)
        self.assertNotEqual(written_data["timestamp"], initial_data["timestamp"])
        self.assertEqual(written_data["clusters"], initial_data["clusters"])

    @patch("service.util.buffer_util.ClusterService.get_csv_buffer_result_path")
    def test_update_buffer_timestamp_file_missing(self, mock_get_path):
        mock_get_path.return_value = Path("missing.json")
        with patch("pathlib.Path.exists", return_value=False):
            buffer_util.update_buffer_timestamp()  # Should log a warning, not crash
