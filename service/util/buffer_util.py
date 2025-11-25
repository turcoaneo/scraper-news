# service/util/buffer_util.py

import json
from datetime import datetime

from app.utils.env_vars import APP_ENV
from app.utils.env_vars import S3_BUCKET, S3_PREFIX
from service.cluster_service import ClusterService
from service.util.logger_util import get_logger
from service.util.s3_util import S3Util

s3_util = S3Util(S3_BUCKET, S3_PREFIX)
logger = get_logger()


def update_buffer_timestamp():
    try:
        if APP_ENV == "uat":
            _update_buffer_timestamp_s3()
        else:
            _update_buffer_timestamp_local()
    except Exception as e:
        logger.error(f"[Buffer] Failed to update timestamp: {e}")


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


def _update_buffer_timestamp_s3():
    def set_timestamp(data: dict) -> dict:
        data["timestamp"] = datetime.now().isoformat()
        return data

    s3_util.patch_json(S3_PREFIX, set_timestamp)
    logger.info(f"[Buffer] Timestamp updated in S3: {S3_PREFIX}")


def _update_delta_timestamp_s3():
    key = get_s3_delta_path()
    payload = {"delta": datetime.now().isoformat()}
    s3_util.write_json(key, payload)


def _read_delta_timestamp_s3():
    key = get_s3_delta_path()
    data = s3_util.read_json(key)
    return data.get("delta") if data else None


def _delete_delta_file_s3():
    key = get_s3_delta_path()
    s3_util.delete_object(key)
