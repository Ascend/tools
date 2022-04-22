import unittest
from unittest.mock import patch
import ada_prof_cmd
import sys
from ada_pa_base_unittest import *
from collections import defaultdict


def load_tracing_file(name, index):
    with open(get_test_file("{}_tracing_{}.json".format(name, index)), 'r') as f:
        return json.load(f)


def load_summary_file(name, index):
    with open(get_test_file("{}_summary_{}.csv".format(name, index)), 'r') as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


def load_op_statistics_file(name, index):
    with open(get_test_file("{}_op_stat_{}.csv".format(name, index)), 'r') as f:
        reader = csv.DictReader(f)
        return [row for row in reader]


class TracingChecker(unittest.TestCase):
    def __init__(self, tracing):
        super().__init__()
        self._tracing = tracing

    def assert_events_num(self, num):
        self.assertEqual(len(self._tracing), num)

    def assert_events_dur(self, event_name, durs):
        tracing_durs = []
        for event in self._tracing:
            if event["name"] == event_name:
                tracing_durs.append(event["dur"])
        self.assertEqual(len(tracing_durs), len(durs))
        for i in range(len(durs)):
            self.assertAlmostEqual(tracing_durs[i], durs[i])


class SummaryChecker(unittest.TestCase):
    def __init__(self, summary):
        super().__init__()
        self._summary = {}
        for data in summary:
            self._summary[data['event']] = data

    def assert_event_dur(self, event_name, dur):
        self.assertTrue(event_name in self._summary)
        self.assertAlmostEqual(float(self._summary[event_name]['avg(us)']), dur)

    def assert_event_count(self, event_name, count):
        self.assertTrue(event_name in self._summary)
        self.assertAlmostEqual(int(self._summary[event_name]['count']), count)

    def w_percent_check(self, standard_event="[AclCompileAndExecute]"):
        if not standard_event in self._summary:
            return
        standard_dur = float(self._summary[standard_event]['total(us)'])
        for data in self._summary.values():
            self.assertAlmostEqual(float(data['total(us)']) / standard_dur, float(data['w-percent']))


class OpStatChecker(unittest.TestCase):
    def __init__(self, statistics):
        super().__init__()
        self._stat = defaultdict(list)
        for row in statistics:
            self._stat[OpStatChecker.get_id(row['name'], row['event'])].append(float(row['duration(us)']))

    @staticmethod
    def get_id(node_name, event_name):
        return "{}@{}".format(node_name, event_name)

    def assert_durs(self, node_name, event_name, durations):
        key = OpStatChecker.get_id(node_name, event_name)
        self.assertTrue(key in self._stat)
        self.assertEqual(len(self._stat[key]), len(durations))
        for i in range(len(durations)):
            self.assertAlmostEqual(self._stat[key][i], durations[i])


class AdaPaUt(AdaPaBaseUt):
    def assert_result_file_exists(self, prefix, num):
        for i in range(num):
            path = get_test_file("{}_summary_{}.csv".format(prefix, i))
            self.assertTrue(os.path.isfile(path))

            path = get_test_file("{}_tracing_{}.json".format(prefix, i))
            self.assertTrue(os.path.isfile(path))

            path = get_test_file("{}_op_stat_{}.csv".format(prefix, i))
            self.assertTrue(os.path.isfile(path))

    def assert_events_num(self, tracing, num):
        self.assertEqual(len(tracing), num)

    def assert_events_dur(self, tracing, event_name, durs):
        tracing_durs = []
        for event in tracing:
            if event["name"] == event_name:
                tracing_durs.append(event["dur"])
        self.assertEqual(len(tracing_durs), len(durs))
        for i in range(len(durs)):
            self.assertAlmostEqual(tracing_durs[i], durs[i])

    def test_analyse_single_prof_data(self):
        log_file = get_test_file("sn0.log")
        with patch.object(sys, 'argv', ['ada-pa', log_file]):
            ada_prof_cmd.main()
        self.assert_result_file_exists("sn0", 1)
        tracing = load_tracing_file("sn0", 0)
        tracing_checker = TracingChecker(tracing)
        tracing_checker.assert_events_num(12)
        tracing_checker.assert_events_dur("[GatherV2]@[ConstPrepare]", [12.36])
        tracing_checker.assert_events_dur("[UpdateShape]", [2.55, 1.67])
        tracing_checker.assert_events_dur("[rtKernelLaunch]", [18.53, 21.19])

        summary = load_summary_file("sn0", 0)
        summary_checker = SummaryChecker(summary)
        summary_checker.assert_event_dur("[ConstPrepare]", 10.475)
        summary_checker.assert_event_dur("[UpdateShape]", 2.11)
        summary_checker.assert_event_dur("[rtKernelLaunch]", 19.86)
        summary_checker.assert_event_count("[ConstPrepare]", 2)
        summary_checker.assert_event_count("[UpdateShape]", 2)
        summary_checker.assert_event_count("[rtKernelLaunch]", 2)
        summary_checker.w_percent_check("[OpExecute]")

        stat = load_op_statistics_file("sn0", 0)
        stat_checker = OpStatChecker(stat)
        stat_checker.assert_durs("[GatherV2]", "[ConstPrepare]", [12.36])
        stat_checker.assert_durs("[GatherV2]", "[UpdateShape]", [2.55])
        stat_checker.assert_durs("[GatherV2]", "[Tiling]", [20.32])
        stat_checker.assert_durs("[Mul]", "[Tiling]", [20.12])

    def test_analyse_single_prof_data_aclopcompileandexecute(self):
        log_file = get_test_file("sn4.log")
        with patch.object(sys, 'argv', ['ada-pa', log_file]):
            ada_prof_cmd.main()
        self.assert_result_file_exists("sn4", 1)

        summary = load_summary_file("sn4", 0)
        summary_checker = SummaryChecker(summary)
        summary_checker.w_percent_check()


    def test_analyse_single_prof_for_op_stat(self):
        log_file = get_test_file("sn3.log")
        with patch.object(sys, 'argv', ['ada-pa', log_file]):
            ada_prof_cmd.main()
        self.assert_result_file_exists("sn3", 1)

        stat = load_op_statistics_file("sn3", 0)
        stat_checker = OpStatChecker(stat)
        stat_checker.assert_durs("[Transpose]", "[AclMatchStaticOpModel]", [1.594])
        stat_checker.assert_durs("[trans_TransData_85]", "[InferShape]", [12.891])
        stat_checker.assert_durs("[Identity]", "[Tiling]", [18.289])

    def test_analyse_single_prof_data_large(self):
        log_file = get_test_file("sn2.log")
        with patch.object(sys, 'argv', ['ada-pa', log_file]):
            ada_prof_cmd.main()
        self.assert_result_file_exists("sn2", 1)
        tracing = load_tracing_file("sn2", 0)
        self.assert_events_num(tracing, 24862)
        self.assert_events_dur(tracing, "[GatherV2]@[AclCompileAndExecute]", [114.09, 69.826, 43.023, 40.215])
        self.assert_events_dur(tracing, "[MatMul]@[Tiling]", [35.266, 24.663, 22.501])

    def test_analyse_multiple_prof_data(self):
        log_file = get_test_file("sn1.log")
        with patch.object(sys, 'argv', ['ada-pa', log_file]):
            ada_prof_cmd.main()
        self.assert_result_file_exists("sn1", 2)


if __name__ == '__main__':
    unittest.main()
