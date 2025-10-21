# service/util/timing_util.py
import time
from functools import wraps


def elapsed_time(label=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = label or func.__name__
            print(f"[{name}] started")
            start = time.time()
            result = func(*args, **kwargs)
            duration = time.time() - start
            print(f"[{name}] completed in {duration:.3f}s")
            return result

        return wrapper

    return decorator
