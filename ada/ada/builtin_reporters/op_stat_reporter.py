from ada.definitions import *
from ada.reporter_registry import reporter
import csv
from collections import defaultdict


@reporter("opstat")
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
        """
        for pd in self._pds:
            threads_to_unfinished_events = defaultdict(list)
            for event in pd.event_records:
                thread_id = OpStatisticReporter.thread_id(event)
                unfinished_events = threads_to_unfinished_events[thread_id]
                if event.node_name is not None:
                    unfinished_events.append(event)
                    continue
                while len(unfinished_events) > 0:
                    latest_event = unfinished_events[-1]
                    if latest_event.end <= event.start:
                        unfinished_events.pop()
                        continue
                    if latest_event.end < event.end:
                        print("WARNING: Ignore event {}, time range overlapped with {}".format(event, latest_event))
                        continue
                    event.node_name = latest_event.node_name
                    break
                else:
                    print("WARNING: Ignore a no name event {}, because can not find a top event for it".format(event))
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
