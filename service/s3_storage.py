import boto3
from botocore.exceptions import ClientError

from app.utils.env_vars import S3_BUCKET, S3_PREFIX


class S3Storage:
    def __init__(self):
        self.bucket = S3_BUCKET
        self.prefix = S3_PREFIX
        self.client = boto3.client("s3")

    def save(self, filename: str, content: bytes):
        key = f"{self.prefix}/{filename}"
        self.client.put_object(Bucket=self.bucket, Key=key, Body=content)

    def load(self, filename: str) -> bytes:
        key = f"{self.prefix}/{filename}"
        obj = self.client.get_object(Bucket=self.bucket, Key=key)
        return obj["Body"].read()

    def exists(self, filename: str) -> bool:
        key = f"{self.prefix}/{filename}"
        try:
            self.client.head_object(Bucket=self.bucket, Key=key)
            return True
        except ClientError as e:
            if e.response["Error"]["Code"] == "404":
                return False
            raise  # re-raise unexpected errors
