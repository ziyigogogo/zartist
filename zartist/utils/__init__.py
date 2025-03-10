from functools import wraps
import time

from zartist import logger


def fn_timer(n_repeats=1):

    def decorate(func=None):

        @wraps(func)
        def wrapper(*args, **kwargs):
            total_time = 0
            result = None
            for _ in range(n_repeats):
                tic = time.perf_counter()
                result = func(*args, **kwargs)
                toc = time.perf_counter()
                total_time += toc - tic
            avg_time = total_time / n_repeats
            info = f"{func.__qualname__} - average execution time over {n_repeats} run(s): {avg_time:.6f} seconds"
            logger.debug(info)
            return result

        return wrapper

    if callable(n_repeats):
        func, n_repeats = n_repeats, 1
        return decorate(func)

    return decorate
