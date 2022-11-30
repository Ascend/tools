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
