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
