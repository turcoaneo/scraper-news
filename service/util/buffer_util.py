# service/util/buffer_util.py

import json
from datetime import datetime

from service.cluster_service import ClusterService
from service.util.logger_util import get_logger

logger = get_logger()


def update_buffer_timestamp():
    path = ClusterService.get_csv_buffer_result_path()
    try:
        if not path.exists():
            logger.warning(f"[Buffer] No buffer file found at {path}")
            return
        with open(path, "r+", encoding="utf-8") as f:
            data = json.load(f)
            data["timestamp"] = datetime.now().isoformat()
            f.seek(0)
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.truncate()
        logger.info(f"[Buffer] Timestamp updated in {path}")
    except Exception as e:
        logger.error(f"[Buffer] Failed to update timestamp: {e}")


def get_delta_path():
    return ClusterService.get_csv_buffer_result_path().parent / "delta_run.json"


def update_delta_timestamp():
    path = get_delta_path()
    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"delta": datetime.now().isoformat()}, f, ensure_ascii=False, indent=2)
        logger.info(f"[Buffer] Delta timestamp updated in {path}")
    except Exception as e:
        logger.error(f"[Buffer] Failed to update delta timestamp: {e}")


def read_delta_timestamp():
    path = get_delta_path()
    if not path.exists():
        return None
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data.get("delta")
    except Exception as e:
        logger.error(f"[Buffer] Failed to read delta timestamp: {e}")
        return None


def delete_delta_file_if_exists():
    path = get_delta_path()
    try:
        if path.exists():
            path.unlink()
            logger.info(f"[Buffer] Deleted delta file at {path}")
        else:
            logger.debug(f"[Buffer] No delta file to delete at {path}")
    except Exception as e:
        logger.error(f"[Buffer] Failed to delete delta file: {e}")
