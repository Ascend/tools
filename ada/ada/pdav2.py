# Profiling Data Analysis version 2
import logging
import os.path
from typing import List
from collections import defaultdict, OrderedDict
import re
import json
import sys
import csv
import copy

# 标准事件，指的是可以标志一次完整下发的事件，这个事件覆盖了一次完整的下发，涵盖在这个事件的时间范围内的其他
STANDARD_EVENTS = ["[AclCompileAndExecute]", "[OpExecute]"]
DEVICE_EVENT = "[Compute]"
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


class ProfilingDataAnalyzer:
    V1_START_RE = re.compile(r'Profiler version: (?P<version>[\d+\.]+), dump start, records num: \d+')
    V1_RE = re.compile(
        r'(?P<timestamp>\d+) (?P<tid>\d+) (?P<element>(\[\S+\])|(UNKNOWN\(-?\d+\))) (?P<event>(\[\S+\])|(UNKNOWN\(-?\d+\))) (?P<et>(Start)|(End)|(UNKNOWN\(-?\d+\)))')

    def __init__(self, file_path):
        self._file_path = file_path

    def read_in_records(self):
        pds = []
        with open(self._file_path, 'r') as f:
            pd = ProfilingData()
            for line in f:
                ma = ProfilingDataAnalyzer.V1_START_RE.match(line)
                if ma is not None:
                    pd.version = ma.group('version')
                    continue
                if line.startswith("Profiling dump end"):
                    pds.append(pd)
                    pd = ProfilingData()
                    continue
                ma = ProfilingDataAnalyzer.V1_RE.match(line)
                if ma is not None:
                    rec = Record()
                    rec.timestamp = int(ma.group("timestamp"))
                    rec.tid = int(ma.group("tid"))
                    rec.node_name = ma.group("element")
                    if rec.node_name.startswith("UNKNOWN"):
                        rec.node_name = None
                    rec.event = ma.group("event")
                    if rec.event == DEVICE_EVENT:
                        rec.device = DEV_DEVICE
                        rec.tid = 1
                    rec.et = ma.group("et")
                    pd.add_record(rec)
                    continue
                # logging.warning("Skip unrecognized line {}".format(line))
        return pds

    @staticmethod
    def read_in_event_records(pds: [ProfilingData]):
        for pd in pds:
            records = pd.records[:]
            records.sort(key=lambda rec: rec.timestamp)
            keys_to_starts = defaultdict(list)
            for rec in records:
                name = get_name(rec)
                if rec.et == 'Start':
                    keys_to_starts[name].append(rec)
                    continue
                if rec.et == 'End':
                    if len(keys_to_starts[name]) == 0:
                        print("WARNING: Drop record {}, because can not find a start record for it".format(rec))
                        continue
                    start_rec = keys_to_starts[name].pop()
                    er = EventRecord.create_from_rec(start_rec)
                    er.start = start_rec.timestamp
                    er.end = rec.timestamp
                    pd.add_event_record(er)
            for starts in keys_to_starts.values():
                for no_end_start_rec in starts:
                    print("WARNING: Drop record {}, because can not find a end event for it".format(no_end_start_rec))

    def read_in_profiling_file(self):
        pds = self.read_in_records()
        ProfilingDataAnalyzer.read_in_event_records(pds)
        return pds


def get_name(rec: Record):
    if rec.node_name is None:
        return rec.event
    else:
        return "{}@{}".format(rec.node_name, rec.event)


class TracingReporter:
    def __init__(self, pds: [ProfilingData]):
        self._pds = pds

    def report(self, file_path):
        for i, pd in enumerate(self._pds):
            j_file = []
            for rec in pd.event_records:
                j_rec = {
                    "name": get_name(rec),
                    "ph": "X",
                    "pid": rec.device,
                    "tid": rec.tid,
                    "ts": rec.start / 1000,
                    "dur": (rec.end - rec.start) / 1000
                }

                j_file.append(j_rec)

            dump_path = "{}_tracing_{}{}".format(file_path, i, ".json")
            print("Dump to tracing file {}".format(dump_path))
            with open(dump_path, "w") as f:
                json.dump(j_file, f)


class OpStatisticReporter:
    """表格中的内容为：
    |op name|event|duration|
    """
    def __init__(self, pds: [ProfilingData]):
        self._pds = pds[:]

    @staticmethod
    def thread_id(event):
        return "{}-{}".format(event.device, event.tid)

    def confirm_all_events_node_name(self):
        """本函数的关键算法是要基于时间范围，确定一个event的node_name。每个event都有一个开始和结束时间戳，
        对于一个event A的开始和结束时间戳记为:A-start, A-end。

        如果对于event A和event B，满足如下几个条件，则认为A-node_name = B-node_name：
        1. A与B发生在相同的thread上
        2. A-start > B-Start && A-end < B-end
        3. A-node_name is None

        如果对于event A、B、C三个event中，A与B，A与C都满足上述条件，且A-node_name is None，
        那么A-node_name取B和C中距离其较近的event的node-name(“较近的”这个定义就不展开了，应该是明确的吧？)

        本函数的算法思路：
        1. 按照start时间戳，对所有的event排序
        2. 整个算法会从前向后遍历一次所有的event，不需要多次遍历
        3. 遍历过程中，维护一个unfinished_events，表达截止到当前遍历的event为止，end > CURRENT_EVENT-start的所有遍历过的event
        4. unfinished_events可以简单理解为一个有序list，以end时间戳排序
        5. 遍历到一个有node_name的event时，将其加入到unfinished_events中
        6. 遍历到一个无node_name的event时，如果unfinished_events为空，则无法判断此event的node_name
        7. 遍历到一个无node_name的event时，如果unfinished_events不为空，则取其中第一个event的node_name
        """
        for pd in self._pds:
            pd.event_records.sort(key=lambda rec: rec.start)
            threads_to_unfinished_events = defaultdict(list)
            for event in pd.event_records:
                thread_id = OpStatisticReporter.thread_id(event)
                unfinished_events = threads_to_unfinished_events[thread_id]
                if event.node_name is not None:
                    unfinished_events.append(event)
                    continue

                # remove all events finished
                unfinished_events = list(filter(lambda ev: ev.end > event.start, unfinished_events))
                if len(unfinished_events) == 0:
                    print("WARNING: Drop a no name event {}, because can not find a top event for it".format(event))
                    continue

                unfinished_events.sort(key=lambda ev: ev.end)
                event.node_name = unfinished_events[0].node_name
        return self._pds

    def report(self, path):
        self.confirm_all_events_node_name()
        for i, pd in enumerate(self._pds):
            statistics = []
            for event in pd.event_records:
                statistics.append({
                    "name": event.node_name,
                    "event": event.event,
                    "duration(us)": (event.end - event.start) / 1000
                })
            dump_path = "{}_op_stat_{}.csv".format(path, i)
            print("Dump to op statistic file {}".format(dump_path))
            with open(dump_path, "w", newline='') as f:
                cf = csv.DictWriter(f, fieldnames=["name", "event", "duration(us)"])
                cf.writeheader()
                cf.writerows(statistics)


class SummaryReporter:
    """表格中有如下内容：
    |流程类型|调用次数|平均时长|加权平均|加权后占比|
    """

    def __init__(self, pds: [ProfilingData]):
        self._pds = pds[:]
        for pd in self._pds:
            pd.records.sort(key=lambda rec: rec.timestamp)

    def read_in_events(self):
        events = []
        for pd in self._pds:
            events_to_time_len = defaultdict(list)
            for rec in pd.event_records:
                if rec.device != DEV_HOST_CPU:
                    continue
                name = rec.event
                events_to_time_len[name].append((rec.end - rec.start) / 1000)
            events.append(events_to_time_len)
        return events

    def get_standard_dur(self, events_to_time_len):
        for standard_event in STANDARD_EVENTS:
            total_time_len = sum(events_to_time_len.get(standard_event, []))
            if total_time_len != 0:
                return total_time_len
        return 0


    def report(self, path):
        events = self.read_in_events()
        for i, events_to_time_len in enumerate(events):
            summary = []
            total_time_len = self.get_standard_dur(events_to_time_len)
            if total_time_len == 0:
                print("WARNING: Missing standard event, Can not generate the weighted percent")
            for event, time_lens in events_to_time_len.items():
                j = {
                    "event": event,
                    "count": len(time_lens),
                    "avg(us)": sum(time_lens) / len(time_lens),
                    "total(us)": sum(time_lens),
                    "w-percent": 0
                }
                if total_time_len != 0:
                    j["w-percent"] = sum(time_lens) / total_time_len
                summary.append(j)

            dump_path = "{}_summary_{}{}".format(path, i, ".csv")
            print("Dump to summary file {}".format(dump_path))
            with open(dump_path, "w", newline='') as f:
                cf = csv.DictWriter(f, fieldnames=["event", "count", "avg(us)", "total(us)", "w-percent"])
                cf.writeheader()
                cf.writerows(summary)


def main_ge(args):
    path, tracing_path, reporter_files = args.input_file, args.output, args.reporter
    analyzer = ProfilingDataAnalyzer(path)
    pds = analyzer.read_in_profiling_file()

    reporter = TracingReporter(pds)
    reporter.report(tracing_path)

    reporter = SummaryReporter(pds)
    reporter.report(tracing_path)

    reporter = OpStatisticReporter(pds)
    reporter.report(tracing_path)

    if reporter_files is not None:
        for reporter_file in reporter_files:
            reporter_file = os.path.realpath(reporter_file)
            path_name = os.path.dirname(reporter_file)
            if path_name not in sys.path:
                sys.path.append(path_name)
            module_name = os.path.splitext(os.path.basename(reporter_file))[0]
            module = __import__(module_name, reporter_file)
            module.report(pds, tracing_path)


class StepProf:
    def __init__(self):
        self.epoch_no = -1
        self.step_no = -1
        self.time_cost = -1
        self.input_shape = []

    def __str__(self):
        return "epoch {}, step {}, shape {}, time {} ms". \
            format(self.epoch_no, self.step_no, self.input_shape, self.time_cost)


def match_and_fill(lines, start, re_obj, fill):
    while start < len(lines):
        ma = re_obj.match(lines[start])
        start += 1
        if ma is not None:
            fill(ma)
            return start
    return start


def match_shape(lines, start, step_prof: StepProf):
    return match_and_fill(lines, start,
                          re.compile(r'torch.Size\(\[(?P<shape>\d+(, \d+)*)\]\)'),
                          lambda ma: step_prof.input_shape.append(ma.group('shape')))


def match_iteration(lines, start, step_prof: StepProf):
    def fill_func(ma):
        step_prof.step_no = int(ma.group('step'))
        step_prof.time_cost = float(ma.group('time'))

    return match_and_fill(lines, start,
                          re.compile(r'iteration\s+(?P<step>\d+)\s+time\s+=\s+(?P<time>\d+(\.\d+)?)\s+ms'),
                          fill_func)


def match_epoch(lines, start, step_prof: StepProf):
    def fill_func(ma):
        step_prof.epoch_no = int(ma.group('epoch'))

    return match_and_fill(lines, start,
                          re.compile(r'\| epoch (?P<epoch>\d+):\s*\d+\s*/\s*\d+.*'),
                          fill_func)


def read_in_step(lines, start):
    prof = StepProf()
    start = match_shape(lines, start, prof)
    start = match_shape(lines, start, prof)
    start = match_iteration(lines, start, prof)
    start = match_epoch(lines, start, prof)
    return start, prof


def read_in_steps_stat(path, stat_path, epoch):
    """从console打印中解析处每个step的执行时长、shape等信息"""
    epoch = int(epoch)
    with open(path, 'r') as f:
        lines = f.readlines()
    current_line = 0
    steps = []
    while current_line < len(lines):
        current_line, step_prof = read_in_step(lines, current_line)
        if step_prof is None:
            break
        if step_prof.epoch_no == epoch:
            steps.append(step_prof)
            print(step_prof)

    with open(stat_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['epoch', 'step', 'shape1', 'shape2', 'time'])
        writer.writeheader()
        for step in steps:
            writer.writerow({'epoch': step.epoch_no,
                             'step': step.step_no,
                             'shape1': int(step.input_shape[0].split(',')[1]),
                             'shape2': int(step.input_shape[1].split(',')[1]),
                             'time': step.time_cost})

    return steps


if __name__ == "__main__":
    # read_in_steps_stat(sys.argv[1], "{}.csv".format(sys.argv[1]), sys.argv[2])
    main_ge(sys.argv[1], sys.argv[2])
