import unittest
import os
from ada.builtin_reporters.op_stat_reporter import OpStatisticReporter
from ada.pdav2 import ProfilingDataAnalyzer
from op_stat_checker import OpStatChecker
from test_pdav2_system import AdaPaSystemTest


class OpStatReporterTestCase(unittest.TestCase):
    log_dir = os.path.realpath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "ada_perf_data"))
    result_dir = os.path.realpath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp-output"))

    def tearDown(self) -> None:
        super().tearDown()
        AdaPaSystemTest.clear()

    def test_match_none_node_name(self):
        pds = ProfilingDataAnalyzer(
            os.path.join(OpStatReporterTestCase.log_dir, "pytorch_acl.log")).read_in_profiling_file()
        OpStatisticReporter(pds).report(os.path.join(OpStatReporterTestCase.result_dir, "t1"))
        result_file_path = os.path.join(OpStatReporterTestCase.result_dir, "t1_op_stat_0.csv")
        records = OpStatChecker().init(result_file_path).FindRecords("[AsStrided]", "[AclMatchOpModel]")
        self.assertEqual(len(records), 3)
        self.assertAlmostEqual(float(records[0]['duration(us)']), 23.72)
        self.assertAlmostEqual(float(records[1]['duration(us)']), 10.95)
        self.assertAlmostEqual(float(records[2]['duration(us)']), 16.8)

        records = OpStatChecker().init(result_file_path).FindRecords("[AxpyV2]", "[AclMatchOpModel]")
        self.assertEqual(len(records), 1)
        self.assertAlmostEqual(float(records[0]['duration(us)']), 7.84)


if __name__ == '__main__':
    unittest.main()
