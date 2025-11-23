# service/cluster_buffer_service.py

import json

from app.routes.cluster_filter_request import ClusterFilterRequest
from app.utils.env_vars import APP_ENV
from service.util.buffer_util import read_delta_timestamp
from service.util.cluster_filter_util import ClusterFilterUtil
from service.util.logger_util import get_logger
from service.s3_storage import S3Storage

logger = get_logger()
storage = S3Storage() if APP_ENV == "uat" else None


class ClusterBufferService:

    @staticmethod
    def get_cached_filtered_clusters(request_filter: ClusterFilterRequest) -> dict:
        data = ClusterBufferService._load_buffer_data()
        if not data:
            return {"error": "Buffer not available"}

        filtered_clusters = ClusterFilterUtil.apply_filter(
            data["clusters"],
            request_filter.filter_places,
            request_filter.filter_including,
            request_filter.filter_excluding
        )

        return ClusterBufferService._attach_delta({
            "timestamp": data["timestamp"],
            "clusters": filtered_clusters
        })

    @staticmethod
    def get_cached_clusters():
        data = ClusterBufferService._load_buffer_data()
        if not data:
            return {"error": "Buffer not available or malformed"}

        return ClusterBufferService._attach_delta(data)

    @staticmethod
    def _load_buffer_data() -> dict:
        try:
            if APP_ENV == "uat":
                raw = storage.load("buffer.json")
                if not raw:
                    logger.warning("Buffer file not found in S3")
                    return {}
                data = json.loads(raw.decode("utf-8"))
            else:
                buffer_path = ClusterBufferService._get_buffer_path()
                if not buffer_path.exists():
                    logger.warning(f"Buffer file not found: {buffer_path}")
                    return {}
                with open(buffer_path, "r", encoding="utf-8", newline="") as f:
                    data = json.load(f)

            if "timestamp" not in data or "clusters" not in data:
                logger.warning("Buffer file is malformed")
                return {}
            return data

        except Exception as e:
            logger.error(f"Failed to read buffer: {e}")
            return {}

    @staticmethod
    def _attach_delta(data: dict) -> dict:
        delta_ts = read_delta_timestamp()
        if delta_ts:
            data["delta"] = delta_ts
        return data

    @staticmethod
    def _get_buffer_path():
        from service.cluster_service import ClusterService
        return ClusterService.get_csv_buffer_result_path()
