import copy
from typing import List

DEV_HOST_CPU = "Host CPU"
DEV_DEVICE = "Device"


class Record:
    def __init__(self):
        self.node_name: str = None
        self.event: str = None
        self.et: str = None
        self.tid: int = None
        self.timestamp: int = None
        self.iteration: str = None
        self.device: str = DEV_HOST_CPU

    def __str__(self):
        return "{}, Thread {}@{}, timestamp {}".format(get_name(self), self.tid, self.device, self.timestamp)


def get_name(rec: Record):
    if rec.node_name is None:
        return rec.event
    else:
        return "{}@{}".format(rec.node_name, rec.event)


class EventRecord(Record):
    def __init__(self):
        super().__init__()
        self.start: int = None
        self.end: int = None

    def __str__(self):
        return "{}, Thread {}@{}, start {}, end {}".format(
            get_name(self), self.tid, self.device, self.start, self.end)

    @staticmethod
    def create_from_rec(rec: Record):
        er = EventRecord()
        er.__dict__ = copy.deepcopy(rec.__dict__)
        return er


class ProfilingData:
    def __init__(self):
        self.version: str = "1.0"
        self.records: List[Record] = []
        self.event_records: List[EventRecord] = []

    def add_record(self, rec: Record):
        self.records.append(rec)

    def add_event_record(self, rec: EventRecord):
        self.event_records.append(rec)


class AdaError(Exception):
    def __init__(self, message):
        self.message = message
