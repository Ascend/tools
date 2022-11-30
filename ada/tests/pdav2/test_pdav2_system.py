import os.path
import unittest
from unittest.mock import patch
import sys
import json
import shutil
import ada_prof_cmd
import csv
from .summary_checker import SummaryChecker


class AdaPaSystemTest(unittest.TestCase):
    log_dir = os.path.realpath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "ada_perf_data"))
    result_dir = os.path.realpath(os.path.join(os.path.dirname(os.path.dirname(__file__)), "temp-output"))

    def tearDown(self) -> None:
        super().tearDown()
        AdaPaSystemTest.clear()

    @staticmethod
    def clear():
        for file_name in os.listdir(AdaPaSystemTest.result_dir):
            if file_name == ".gitkeep":
                continue
            file_path = os.path.join(AdaPaSystemTest.result_dir, file_name)
            if os.path.isfile(file_path):
                os.remove(file_path)
            else:
                shutil.rmtree(os.path.join(AdaPaSystemTest.result_dir, file_name))

    def assert_show_in_ns(self, result_file_path):
        with open(result_file_path, "r") as f:
            jf = json.load(f)
        self.assertTrue("displayTimeUnit" in jf)
        self.assertEqual(jf["displayTimeUnit"], "ns")

    def assert_records_num(self, file_path, num):
        with open(file_path, "r") as f:
            jf = json.load(f)
        self.assertTrue("traceEvents" in jf)
        self.assertEqual(len(jf["traceEvents"]), num)

    def test_default_reports(self):
        with patch.object(sys, 'argv', ["ada-pa",
                                        os.path.join(AdaPaSystemTest.log_dir, "pytorch_ns.log"),
                                        "--output={}".format(AdaPaSystemTest.result_dir)]):
            self.assertEqual(ada_prof_cmd.main(), 0)
        self.assertTrue(os.path.isfile(os.path.join(AdaPaSystemTest.result_dir, "pytorch_ns_tracing_0.json")))
        self.assertTrue(os.path.isfile(os.path.join(AdaPaSystemTest.result_dir, "pytorch_ns_summary_0.csv")))
        self.assertTrue(os.path.isfile(os.path.join(AdaPaSystemTest.result_dir, "pytorch_ns_op_stat_0.csv")))
        self.assertEqual(len(os.listdir(AdaPaSystemTest.result_dir)), 4)

    def test_report_trace(self):
        with patch.object(sys, 'argv', ["ada-pa",
                                        os.path.join(AdaPaSystemTest.log_dir, "pytorch_ns.log"),
                                        "--output={}".format(AdaPaSystemTest.result_dir),
                                        "--reporter=trace"]):
            self.assertEqual(ada_prof_cmd.main(), 0)
        result_file_path = os.path.join(AdaPaSystemTest.result_dir, "pytorch_ns_tracing_0.json")
        self.assertTrue(os.path.isfile(result_file_path))

        self.assert_show_in_ns(result_file_path)
        self.assert_records_num(result_file_path, 249)

    def test_report_summary(self):
        with patch.object(sys, 'argv', ["ada-pa",
                                        os.path.join(AdaPaSystemTest.log_dir, "pytorch_ns.log"),
                                        "--output={}".format(AdaPaSystemTest.result_dir),
                                        "--reporter=summary"]):
            self.assertEqual(ada_prof_cmd.main(), 0)
        result_file_path = os.path.join(AdaPaSystemTest.result_dir, "pytorch_ns_summary_0.csv")
        SummaryChecker().execute_count(7).check(result_file_path)

    def summary_self_consistent(self, path, index):
        single_op_summary = os.path.join(os.path.dirname(path), "single-op",
                                         f"{os.path.basename(path)}_single_op_summary_{index}.csv")
        self.assertTrue(os.path.isfile(single_op_summary))
        with open(single_op_summary, 'r') as f:
            cf = csv.DictReader(f)
            for row in cf:
                if row['execution_type'] == "all":
                    total_count = row['count']
                    total_time = row['total(us)']

        summary = f"{path}_summary_{index}.csv"
        self.assertTrue(os.path.isfile(summary))
        with open(summary, 'r') as f:
            cf = csv.DictReader(f)
            for row in cf:
                if row['event'] == "[Execute]":
                    summary_total_count = row['count']
                    summary_total_time = row['total(us)']

        self.assertEqual(total_count, summary_total_count)
        self.assertAlmostEqual(total_time, summary_total_time)

    def test_single_op_summary(self):
        with patch.object(sys, 'argv', ["ada-pa",
                                        os.path.join(AdaPaSystemTest.log_dir, "pytorch_ns.log"),
                                        "--output={}".format(AdaPaSystemTest.result_dir),
                                        "--reporter=single-op"]):
            self.assertEqual(ada_prof_cmd.main(), 0)
        result_file_path = os.path.join(AdaPaSystemTest.result_dir, "single-op",
                                        "pytorch_ns_aicore_single_op_summary_0.csv")
        SummaryChecker().execute_count(6).check(result_file_path)

        result_file_path = os.path.join(AdaPaSystemTest.result_dir, "single-op", "pytorch_ns_subgraph_summary_0.csv")
        SummaryChecker().execute_count(1).check(result_file_path)

        result_file_path = os.path.join(AdaPaSystemTest.result_dir, "single-op", "pytorch_ns_single_op_summary_0.csv")
        self.summary_self_consistent(os.path.join(AdaPaSystemTest.result_dir, "pytorch_ns"), 0)

        self.assertEqual(len(os.listdir(AdaPaSystemTest.result_dir)), 5)
        self.assertEqual(len(os.listdir(os.path.join(AdaPaSystemTest.result_dir, "single-op"))), 3)


if __name__ == '__main__':
    unittest.main()
