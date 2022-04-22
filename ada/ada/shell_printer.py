import threading


class MessageHolder:
    def __init__(self, msg):
        self._msg = msg

    def set(self, msg):
        self._msg = msg

    def get(self):
        return self._msg


class DotPrinter:
    @staticmethod
    def print_loop(waiter: threading.Condition, start_msg: str, end_msg: MessageHolder):
        print("{} .".format(start_msg), end='', flush=True)
        with waiter:
            while not waiter.wait(1):
                print('.', end='', flush=True)
            print(' {}.'.format(end_msg.get()))

    def __init__(self, start_message=''):
        self._waiter = threading.Condition(threading.Lock())
        self._end_msg = MessageHolder('')
        self._printer = threading.Thread(target=DotPrinter.print_loop,
                                         args=(self._waiter, start_message, self._end_msg))

    def __enter__(self):
        self.start()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.stop()

    def start(self):
        self._printer.start()

    def stop(self, end_msg='Done'):
        with self._waiter:
            self._end_msg.set(end_msg)
            self._waiter.notify()
        self._printer.join()
