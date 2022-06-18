import queue
import time
from queue import Queue
import threading

class QueryInfo:
    def __init__(self, query_id, index, time, valid=True):
        self.query_id = query_id
        self.index = index
        self.time = time
        self.valid = valid

class Scheduler():
    def __init__(self, batchsize=1, proc_func=None, wait_time=0):
        self.batchsize = batchsize
        self.queue = Queue(maxsize=100000)
        self.workers = []
        self.con = threading.Condition()
        self.proc_func = proc_func
        self.cursample = None
        self.wait_time = wait_time
        print("schedule wait time", wait_time)

        worker = threading.Thread(target=self.scheduler_tasks)
        worker.daemon = True
        self.workers.append(worker)
        worker.start()

    def enqueue(self, query_id, index):
        self.con.acquire()
        self.queue.put(QueryInfo(query_id, index))
        self.con.notify()
        self.con.release()

    def reassemble_batchsamples(self):
        batchsamples = [self.cursample]
        for _ in range(min(self.batchsize-1, self.queue.qsize())):
            batchsamples.append(self.queue.get())
        count = self.batchsize - len(batchsamples)
        for _ in range(count):
            batchsamples.append(QueryInfo(0, 0, False))
        self.proc_func(batchsamples)

    def scheduler_tasks(self):
        self.cursample = None
        while True:
            self.con.acquire()
            if self.cursample is None:
                if self.queue.qsize() == 0:
                    self.con.wait(self.wait_time)
                else:
                    self.cursample = self.queue.get()
            else:
                wait_time = self.cursample.time - time.monotonic() + self.wait_time
                if wait_time > 0 and self.queue.qsize() < self.batchsize:
                    self.con.wait(wait_time)
                else:
                    self.reassemble_batchsamples()
                    self.cursample = None
            self.con.release()
