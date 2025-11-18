import unittest
from unittest.mock import patch, MagicMock

from service.s3_storage import S3Storage


class TestS3Storage(unittest.TestCase):
    @patch("service.s3_storage.boto3.client")
    def test_save_and_load(self, mock_boto_client):
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        storage = S3Storage()
        storage.save("test.csv", b"data123")

        mock_s3.put_object.assert_called_with(
            Bucket="scraper-storage-uat",
            Key="storage/test.csv",
            Body=b"data123"
        )

        mock_s3.get_object.return_value = {"Body": MagicMock(read=lambda: b"data123")}
        result = storage.load("test.csv")
        self.assertEqual(result, b"data123")

    @patch("service.s3_storage.boto3.client")
    def test_exists(self, mock_boto_client):
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        # Mock successful head_object
        storage = S3Storage()
        mock_s3.head_object.return_value = {}
        self.assertTrue(storage.exists("test.csv"))

        # Mock ClientError for missing file
        from botocore.exceptions import ClientError
        mock_s3.head_object.side_effect = ClientError(
            error_response={"Error": {"Code": "404", "Message": "Not Found"}},
            operation_name="HeadObject"
        )
        self.assertFalse(storage.exists("missing.csv"))
