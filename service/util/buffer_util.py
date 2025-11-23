# service/util/buffer_util.py

import json
from datetime import datetime

import boto3

from app.utils.env_vars import APP_ENV, S3_BUCKET, S3_PREFIX
from service.cluster_service import ClusterService
from service.util.logger_util import get_logger

logger = get_logger()


def update_buffer_timestamp():
    try:
        if APP_ENV == "uat":
            _update_buffer_timestamp_s3()
        else:
            _update_buffer_timestamp_local()
    except Exception as e:
        logger.error(f"[Buffer] Failed to update timestamp: {e}")


def _update_buffer_timestamp_s3():
    s3 = boto3.client("s3")
    response = s3.get_object(Bucket=S3_BUCKET, Key=S3_PREFIX)
    data = json.loads(response["Body"].read().decode("utf-8"))

    data["timestamp"] = datetime.now().isoformat()

    s3.put_object(
        Bucket=S3_BUCKET,
        Key=S3_PREFIX,
        Body=json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    )
    logger.info(f"[Buffer] Timestamp updated in S3: {S3_PREFIX}")


def _update_buffer_timestamp_local():
    path = ClusterService.get_csv_buffer_result_path()
    if not path.exists():
        logger.warning(f"[Buffer] No buffer file found at {path}")
        return

    with open(path, "r+", encoding="utf-8", newline="") as f:
        data = json.load(f)
        data["timestamp"] = datetime.now().isoformat()
        f.seek(0)
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.truncate()
    logger.info(f"[Buffer] Timestamp updated in {path}")


def get_delta_path():
    return ClusterService.get_csv_buffer_result_path().parent / "delta_run.json"


def get_s3_delta_path() -> str:
    return S3_PREFIX + "/delta_run.json"


def update_delta_timestamp():
    if APP_ENV == "uat":
        _update_delta_timestamp_s3()
    else:
        path = get_delta_path()
        try:
            with open(path, "w", encoding="utf-8", newline="") as f:
                json.dump({"delta": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)
            logger.info(f"[Buffer] Delta timestamp updated in {path}")
        except Exception as e:
            logger.error(f"[Buffer] Failed to update delta timestamp: {e}")


def read_delta_timestamp():
    if APP_ENV == "uat":
        return _read_delta_timestamp_s3()
    else:
        path = get_delta_path()
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8", newline="") as f:
                data = json.load(f)
            return data.get("delta")
        except Exception as e:
            logger.error(f"[Buffer] Failed to read delta timestamp: {e}")
            return None


def delete_delta_file_if_exists():
    if APP_ENV == "uat":
        _delete_delta_file_s3()
    else:
        path = get_delta_path()
        try:
            if path.exists():
                path.unlink()
                logger.info(f"[Buffer] Deleted delta file at {path}")
            else:
                logger.debug(f"[Buffer] No delta file to delete at {path}")
        except Exception as e:
            logger.error(f"[Buffer] Failed to delete delta file: {e}")


def _update_delta_timestamp_s3():
    s3 = boto3.client("s3")
    key = get_s3_delta_path()
    payload = {"delta": datetime.now().isoformat()}
    s3.put_object(
        Bucket=S3_BUCKET,
        Key=key,
        Body=json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    )
    logger.info(f"[Buffer] Delta timestamp updated in S3: {key}")


def _read_delta_timestamp_s3():
    s3 = boto3.client("s3")
    key = get_s3_delta_path()
    try:
        response = s3.get_object(Bucket=S3_BUCKET, Key=key)
        data = json.loads(response["Body"].read().decode("utf-8"))
        return data.get("delta")
    except s3.exceptions.NoSuchKey:
        return None
    except Exception as e:
        logger.error(f"[Buffer] Failed to read delta timestamp from S3: {e}")
        return None


def _delete_delta_file_s3():
    s3 = boto3.client("s3")
    key = get_s3_delta_path()
    try:
        s3.delete_object(Bucket=S3_BUCKET, Key=key)
        logger.info(f"[Buffer] Deleted delta file in S3: {key}")
    except s3.exceptions.NoSuchKey:
        logger.debug(f"[Buffer] No delta file to delete in S3: {key}")
    except Exception as e:
        logger.error(f"[Buffer] Failed to delete delta file from S3: {e}")
