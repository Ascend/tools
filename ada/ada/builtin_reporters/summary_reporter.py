from ada.reporter_registry import reporter
from ada.definitions import *
from collections import defaultdict
import csv


STANDARD_EVENTS = ["[AclCompileAndExecute]", "[OpExecute]", "[Execute]"]


@reporter("summary")
class SummaryReporter:
    """表格中有如下内容：
    |流程类型|调用次数|平均时长|加权平均|加权后占比|
    """

    def __init__(self, pds: [ProfilingData]):
        self._pds = pds[:]

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

    @staticmethod
    def get_standard_dur(events_to_time_len):
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
