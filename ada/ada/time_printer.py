import time


class TimePrinter:
    def __init__(self, prefix, print_threshold=10):
        self._prefix = prefix
        self._threshold = print_threshold
        self._start = time.perf_counter()

    def __enter__(self):
        print("Begin to {}...".format(self._prefix))
        self._start = time.perf_counter()

    def __exit__(self, exc_type, exc_val, exc_tb):
        dur = time.perf_counter() - self._start
        if dur > self._threshold:
            print("Finish to {}, time cost {} seconds".format(self._prefix, dur))
