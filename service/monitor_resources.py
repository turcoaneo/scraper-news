import threading
import time
import psutil

from service.util.logger_util import get_logger

logger = get_logger()


def monitor_resources(interval=10):
    process = psutil.Process()
    while True:
        mem_mb = process.memory_info().rss / 1024 ** 2
        cpu_percent = process.cpu_percent(interval=1)
        logger.warning(f"[RESOURCE] Memory: {mem_mb:.2f} MB | CPU: {cpu_percent:.2f}%")
        time.sleep(interval - 1)  # subtract the 1s used by cpu_percent
        if mem_mb > 1500:
            logger.warning("Warning: Memory usage approaching ECS limit!")


# Start the monitor in the background
threading.Thread(target=lambda: time.sleep(5) or monitor_resources(10), daemon=True).start()
