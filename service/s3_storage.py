import boto3
from botocore.exceptions import ClientError

from app.utils.env_vars import merged


class S3Storage:
    def __init__(self):
        self.bucket = merged.get("S3_BUCKET", "scraper-storage-uat")
        self.prefix = merged.get("S3_PREFIX", "storage/")
        self.client = boto3.client("s3")

    def save(self, filename: str, content: bytes):
        key = f"{self.prefix}{filename}"
        self.client.put_object(Bucket=self.bucket, Key=key, Body=content)

    def load(self, filename: str) -> bytes:
        key = f"{self.prefix}{filename}"
        obj = self.client.get_object(Bucket=self.bucket, Key=key)
        return obj["Body"].read()

    def exists(self, filename: str) -> bool:
        key = f"{self.prefix}{filename}"
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise  # re-raise unexpected errors
