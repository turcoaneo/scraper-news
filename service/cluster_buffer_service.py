# service/cluster_buffer_service.py

import json
from app.utils.env_vars import APP_ENV
from service.util.buffer_util import read_delta_timestamp
from service.util.logger_util import get_logger
from service.s3_storage import S3Storage

logger = get_logger()
storage = S3Storage() if APP_ENV == "uat" else None


class ClusterBufferService:

    @staticmethod
    def get_buffer_path():
        from service.cluster_service import ClusterService
        return ClusterService.get_csv_buffer_result_path()

    @staticmethod
    def get_cached_clusters():
        try:
            if APP_ENV == "uat":
                raw = storage.load("buffer.json")
                if not raw:
                    logger.warning("Buffer file not found in S3")
                    return {"error": "Buffer not available"}
                data = json.loads(raw.decode("utf-8"))
            else:
                buffer_path = ClusterBufferService.get_buffer_path()
                if not buffer_path.exists():
                    logger.warning(f"Buffer file not found: {buffer_path}")
                    return {"error": "Buffer not available"}
                with open(buffer_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

            if "timestamp" not in data or "clusters" not in data:
                logger.warning("Buffer file is malformed")
                return {"error": "Buffer malformed"}

            delta_ts = read_delta_timestamp()
            if delta_ts:
                data["delta"] = delta_ts
            return data

        except Exception as e:
            logger.error(f"Failed to read buffer: {e}")
            return {"error": "Buffer read error"}
