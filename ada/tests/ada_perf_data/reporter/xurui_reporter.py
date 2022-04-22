from ada.pdav2 import Record, ProfilingData, get_name
from collections import OrderedDict
from typing import List
import csv


STANDARD_EVENT = "[OpExecute]"


class SERecord:
    """Start-End Record"""
    def __init__(self):
        self.node_name: str = None
        self.event: str = None
        self.et: str = None
        self.tid: int = None
        self.start: int = None
        self.end: int = None
        self.iteration: str = None

    @staticmethod
    def from_record(start: Record, end: Record):
        se_rec = SERecord()
        for attr in dir(end):
            if callable(getattr(end, attr)) or attr.startswith("__"):
                continue
            if attr == "et":
                continue
            if attr == "timestamp":
                se_rec.end = getattr(end, attr)
            else:
                setattr(se_rec, attr, getattr(end, attr))
        se_rec.start = start.timestamp
        se_rec.et = "range"
        return se_rec

    def __str__(self):
        return "{} {} {} -> {}".format(self.node_name, self.event, self.start, self.end)


class SEProfilingData:
    def __init__(self):
        self.records: List[SERecord] = []

    @staticmethod
    def from_profiling_data(pds: List[ProfilingData]):
        results = []
        for pd in pds:
            se_pd = SEProfilingData()
            results.append(se_pd)
            events_to_start_rec = {}
            for rec in pd.records:
                name = get_name(rec)
                if rec.et == 'Start':
                    events_to_start_rec[name] = rec
                else:
                    try:
                        start_rec = events_to_start_rec.pop(name)
                    except KeyError as _:
                        continue
                    se_pd.records.append(SERecord.from_record(start_rec, rec))
        return results


class Ranges:
    def __init__(self):
        self._ranges_to_names = OrderedDict()

    def find_ranges(self, num):
        results = []
        for (start, end), names in self._ranges_to_names.items():
            if start > num:
                break
            if end > num:
                results += names
        return results

    def add_range(self, name, start, end):
        pair = (start, end)
        if pair in self._ranges_to_names:
            self._ranges_to_names[pair].append(name)
        else:
            self._ranges_to_names[pair] = [name, ]


class XrReporter:
    def __init__(self, pds: [ProfilingData]):
        self._pds = SEProfilingData.from_profiling_data(pds)

    @staticmethod
    def analyse_records(pd: SEProfilingData):
        pds_by_execution = []
        for rec in pd.records:
            if rec.event == STANDARD_EVENT:
                ranges = Ranges()
                ranges.add_range("_", rec.start, rec.end)
                pds_by_execution.append((ranges, [rec, ]))

        for rec in pd.records:
            if rec.event != STANDARD_EVENT:
                for pd_by_exe in pds_by_execution:
                    if len(pd_by_exe[0].find_ranges(rec.start)) > 0:
                        pd_by_exe[1].append(rec)
                        break
                else:
                    print("WARNING: record {} does not fit in any execution".format(rec))

        return pds_by_execution

    @staticmethod
    def is_op_execution(records: List[SERecord]):
        tids = set()
        for rec in records:
            tids.add(rec.tid)
        # 单算子执行只有一个线程，因此判断tid就可以了，当前也有其他很多判断方法
        return len(tids) == 1

    @staticmethod
    def read_in_events(pds):
        events = []
        for pd in pds:
            events_to_time_len = {}
            for rec in pd.records:
                name = rec.event
                if name in events_to_time_len:
                    events_to_time_len[name].append((rec.end - rec.start) / 1000)
                else:
                    events_to_time_len[name] = [(rec.end - rec.start) / 1000, ]

            events.append(events_to_time_len)
        return events

    @staticmethod
    def report_to_file(file_path, pds, exe_type):
        events = XrReporter.read_in_events(pds)
        for i, events_to_time_len in enumerate(events):
            summary = []
            total_time_len = sum(events_to_time_len.get(STANDARD_EVENT, []))
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

            dump_path = "{}_summary_{}_{}{}".format(file_path, exe_type, i, ".csv")
            print("Dump to summary file {}".format(dump_path))
            with open(dump_path, "w", newline='') as f:
                cf = csv.DictWriter(f, fieldnames=["event", "count", "avg(us)", "total(us)", "w-percent"])
                cf.writeheader()
                cf.writerows(summary)

    def report(self, file_path):
        op_exe_pds = []
        graph_exe_pds = []
        for pd in self._pds:
            execution_ranges_to_records = XrReporter.analyse_records(pd)
            op_exe_pd = SEProfilingData()
            op_exe_pds.append(op_exe_pd)
            graph_exe_pd = SEProfilingData()
            graph_exe_pds.append(graph_exe_pd)

            for ranges, records in execution_ranges_to_records:
                if XrReporter.is_op_execution(records):
                    op_exe_pd.records += records
                else:
                    graph_exe_pd.records += records
        tmp = XrReporter.read_in_events(op_exe_pds)
        XrReporter.report_to_file(file_path, tmp, "op")
        tmp = XrReporter.read_in_events(graph_exe_pds)
        XrReporter.report_to_file(file_path, tmp, "graph")


def report(pds: [ProfilingData], file_path):
    reporter = XrReporter(pds)
    reporter.report(file_path)
