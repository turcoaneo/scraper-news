import unittest
from unittest.mock import patch, MagicMock

from service.hf_uploader import HuggingFaceUploader


class TestHuggingFaceUploader(unittest.TestCase):
    @patch("service.hf_uploader.HfApi")
    def test_create_repo(self, mock_api_class):
        mock_api = MagicMock()
        mock_api.repo_exists.return_value = False
        mock_api.create_repo.return_value = None
        mock_api_class.return_value = mock_api

        uploader = HuggingFaceUploader(username="test-user", token="fake-token")
        repo_id = uploader.create_repo("test-model")
        self.assertEqual(repo_id, "test-user/test-model")

    @patch("service.hf_uploader.upload_folder")
    @patch("service.hf_uploader.HfApi")
    def test_upload_folder(self, mock_api_class, mock_upload_folder):
        mock_api = MagicMock()
        mock_api.repo_exists.return_value = True
        mock_api_class.return_value = mock_api

        uploader = HuggingFaceUploader(username="test-user", token="fake-token")
        uploader.upload_folder("test-model", "./fake-folder")
        mock_upload_folder.assert_called_once()

    @patch("service.hf_uploader.upload_file")
    @patch("service.hf_uploader.HfApi")
    def test_upload_file(self, mock_api_class, mock_upload_file):
        mock_api = MagicMock()
        mock_api.repo_exists.return_value = True
        mock_api_class.return_value = mock_api

        with patch("os.path.isfile", return_value=True):
            uploader = HuggingFaceUploader(username="test-user", token="fake-token")
            uploader.upload_file("test-model", "./bert_model.pt")
            mock_upload_file.assert_called_once()

    def test_upload_file_missing(self):
        with self.assertRaises(FileNotFoundError):
            uploader = HuggingFaceUploader(username="test-user", token="fake-token")
            uploader.upload_file("test-model", "./missing_file.pt")
