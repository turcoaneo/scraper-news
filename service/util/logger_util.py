# service/util/logger_util.py

import logging
import sys

from app.utils.env_vars import APP_ENV, LOGGING_DEBUG_LEVEL


def get_logger(name="app"):
    logger = logging.getLogger(name)

    # Set level based on environment
    app_env = APP_ENV.lower()
    level = logging.DEBUG if app_env in LOGGING_DEBUG_LEVEL else logging.INFO
    logger.setLevel(level)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(level)  # Make sure handler matches logger level

        formatter = logging.Formatter(
            "[%(asctime)s] [%(levelname)s] [%(threadName)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    return logger
