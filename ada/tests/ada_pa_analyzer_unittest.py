import unittest
from ada_pa_base_unittest import *
from ada.pdav2 import ProfilingDataAnalyzer, ProfilingData


def find_events_by_type(pd: ProfilingData, event_type: str):
    events = []
    for event in pd.event_records:
        if event.event == event_type:
            events.append(event)
    return events


class AdaPaAnalyzerUt(AdaPaBaseUt):
    def test_analyse_none_in_none(self):
        """测试这种场景
        |----Transdata execute----------------------------------------|
        |---一些流程---||---None Tiling----------------------|-others--|
                       |-None Tiling-||-AtomicClean Tiling--|
        """
        log_file = get_test_file("sn4.log")
        analyzer = ProfilingDataAnalyzer(log_file)
        pds = analyzer.read_in_profiling_file()

        self.assertEqual(len(pds), 1)
        tiling_events = find_events_by_type(pds[0], "[Tiling]")
        self.assertEqual(len(tiling_events), 3)
        tiling_events.sort(key=lambda rec: rec.start)
        self.assertEqual(tiling_events[0].start, 1643116796438455862)
        self.assertEqual(tiling_events[0].end, 1643116796438470737)
        self.assertEqual(tiling_events[1].start, 1643116796438456862)
        self.assertEqual(tiling_events[1].end, 1643116796438457737)
        self.assertEqual(tiling_events[2].start, 1643116796438458862)
        self.assertEqual(tiling_events[2].end, 1643116796438459737)
        self.assertIsNone(tiling_events[0].node_name)
        self.assertIsNone(tiling_events[1].node_name)
        self.assertEqual(tiling_events[2].node_name, "[AtomicClean]")

    def test_analyse_top_in_top(self):
        """测试这种场景
        |----Transdata execute---------------------------------------------|
        |---一些流程---||---Transdata Tiling----------------------|-others--|
                       |-Transdata Tiling-||-AtomicClean Tiling--|
        """
        log_file = get_test_file("sn5.log")
        analyzer = ProfilingDataAnalyzer(log_file)
        pds = analyzer.read_in_profiling_file()

        self.assertEqual(len(pds), 1)
        tiling_events = find_events_by_type(pds[0], "[Tiling]")
        self.assertEqual(len(tiling_events), 3)
        tiling_events.sort(key=lambda rec: rec.start)
        self.assertEqual(tiling_events[0].start, 1643116796438455862)
        self.assertEqual(tiling_events[0].end, 1643116796438470737)
        self.assertEqual(tiling_events[1].start, 1643116796438456862)
        self.assertEqual(tiling_events[1].end, 1643116796438457737)
        self.assertEqual(tiling_events[2].start, 1643116796438458862)
        self.assertEqual(tiling_events[2].end, 1643116796438459737)

        self.assertEqual(tiling_events[0].node_name, "[TransData]")
        self.assertEqual(tiling_events[1].node_name, "[TransData]")
        self.assertEqual(tiling_events[2].node_name, "[AtomicClean]")


if __name__ == '__main__':
    unittest.main()
