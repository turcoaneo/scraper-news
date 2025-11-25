# service/util/s3_util.py

import boto3
import json
import csv
import io
from datetime import datetime
from service.util.logger_util import get_logger

logger = get_logger()


class S3Util:
    def __init__(self, bucket: str, prefix: str):
        self.bucket = bucket
        self.prefix = prefix
        self.client = boto3.client("s3")

    def read_json(self, key: str) -> dict | None:
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            return json.loads(response["Body"].read().decode("utf-8"))
        except self.client.exceptions.NoSuchKey:
            logger.debug(f"[S3Util] No such key: {key}")
            return None
        except Exception as e:
            logger.error(f"[S3Util] Failed to read JSON from S3: {e}")
            return None

    def write_json(self, key: str, payload: dict):
        try:
            self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8"),
            )
            logger.info(f"[S3Util] JSON written to S3: {key}")
        except Exception as e:
            logger.error(f"[S3Util] Failed to write JSON to S3: {e}")

    def patch_json(self, key: str, mutator):
        """Load JSON, apply mutator(dict)->dict, then write back."""
        data = self.read_json(key) or {}
        try:
            updated = mutator(data) or data
        except Exception as e:
            logger.error(f"[S3Util] Mutator failed for {key}: {e}")
            return
        self.write_json(key, updated)

    def read_csv(self, key: str) -> list[dict]:
        try:
            response = self.client.get_object(Bucket=self.bucket, Key=key)
            content = response["Body"].read().decode("utf-8")
            reader = csv.DictReader(io.StringIO(content))
            rows = list(reader)
            for row in rows:
                if "timestamp" in row:
                    try:
                        row["timestamp"] = datetime.fromisoformat(row["timestamp"])
                    except Exception:
                        pass
            return rows
        except self.client.exceptions.NoSuchKey:
            logger.debug(f"[S3Util] No such CSV key: {key}")
            return []
        except Exception as e:
            logger.error(f"[S3Util] Failed to read CSV from S3: {e}")
            return []

    def write_csv(self, key: str, csv_data: str):
        try:
            self.client.put_object(
                Bucket=self.bucket,
                Key=key,
                Body=csv_data.encode("utf-8"),
            )
            logger.info(f"[S3Util] CSV written to S3: {key}")
        except Exception as e:
            logger.error(f"[S3Util] Failed to write CSV to S3: {e}")

    def delete_object(self, key: str):
        try:
            self.client.delete_object(Bucket=self.bucket, Key=key)
            logger.info(f"[S3Util] Deleted object in S3: {key}")
        except self.client.exceptions.NoSuchKey:
            logger.debug(f"[S3Util] No object to delete in S3: {key}")
        except Exception as e:
            logger.error(f"[S3Util] Failed to delete object from S3: {e}")
