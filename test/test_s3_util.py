# test/test_s3_util.py

import unittest
from unittest.mock import patch, MagicMock
from service.util.s3_util import S3Util


class TestS3Util(unittest.TestCase):

    def setUp(self):
        self.bucket = "test-bucket"
        self.prefix = "test-prefix"

    @patch("service.util.s3_util.boto3.client")
    def test_write_and_read_json(self, mock_client):
        mock_s3 = MagicMock()
        mock_client.return_value = mock_s3

        util = S3Util(self.bucket, self.prefix)
        util.write_json("test.json", {"foo": "bar"})
        mock_s3.put_object.assert_called_once()

        # Simulate get_object returning JSON
        mock_s3.get_object.return_value = {
            "Body": MagicMock(read=lambda: b'{"foo":"bar"}')
        }
        data = util.read_json("test.json")
        self.assertEqual(data["foo"], "bar")

    @patch("service.util.s3_util.boto3.client")
    def test_write_and_read_csv(self, mock_client):
        mock_s3 = MagicMock()
        mock_client.return_value = mock_s3

        util = S3Util(self.bucket, self.prefix)
        util.write_csv("test.csv", "url,timestamp\nhttp://x,2025-11-25T08:00:00")

        mock_s3.put_object.assert_called_once()

        # Simulate get_object returning CSV
        mock_s3.get_object.return_value = {
            "Body": MagicMock(read=lambda: b"url,timestamp\nhttp://x,2025-11-25T08:00:00")
        }
        rows = util.read_csv("test.csv")
        self.assertEqual(rows[0]["url"], "http://x")

    @patch("service.util.s3_util.boto3.client")
    def test_delete_object(self, mock_client):
        mock_s3 = MagicMock()
        mock_client.return_value = mock_s3

        util = S3Util(self.bucket, self.prefix)
        util.delete_object("test.json")
        mock_s3.delete_object.assert_called_once()

    @patch("service.util.s3_util.boto3.client")
    def test_patch_json(self, mock_client):
        mock_s3 = MagicMock()
        mock_client.return_value = mock_s3

        util = S3Util(self.bucket, self.prefix)

        # Simulate existing JSON in S3
        mock_s3.get_object.return_value = {
            "Body": MagicMock(read=lambda: b'{"foo":"bar"}')
        }

        # Capture what gets written back
        written_payloads = {}

        # noinspection PyPep8Naming
        def fake_put_object(Bucket, Key, Body):
            written_payloads["Bucket"] = Bucket
            written_payloads["Key"] = Key
            written_payloads["Body"] = Body

        mock_s3.put_object.side_effect = fake_put_object

        # Mutator adds a new key
        def mutator(data: dict) -> dict:
            data["baz"] = "qux"
            return data

        util.patch_json("test.json", mutator)

        # Verify put_object was called
        self.assertIn("Body", written_payloads)
        import json
        self.assertEqual(written_payloads["Bucket"], self.bucket)
        self.assertEqual(written_payloads["Key"], "test.json")
        updated = json.loads(written_payloads["Body"].decode("utf-8"))
        self.assertEqual(updated["foo"], "bar")
        self.assertEqual(updated["baz"], "qux")


if __name__ == "__main__":
    unittest.main()
