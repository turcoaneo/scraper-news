import json
from pathlib import Path

from service.util.buffer_util import read_delta_timestamp
from service.util.logger_util import get_logger

logger = get_logger()


class ClusterBufferService:

    @staticmethod
    def get_buffer_path() -> Path:
        from service.cluster_service import ClusterService  # avoid circular import
        return ClusterService.get_storage_path() / "buffer.json"

    @staticmethod
    def get_cached_clusters():
        buffer_path = ClusterBufferService.get_buffer_path()
        if not buffer_path.exists():
            logger.warning(f"Buffer file not found: {buffer_path}")
            return {"error": "Buffer not available"}

        try:
            with open(buffer_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Optional: validate structure
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
