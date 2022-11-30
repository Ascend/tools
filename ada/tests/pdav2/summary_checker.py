import unittest
import csv
import os


class SummaryChecker(unittest.TestCase):
    def execute_count(self, count):
        self._execute_count = count
        return self

    def check(self, path):
        self.assertTrue(os.path.isfile(path))
        with open(path, 'r') as f:
            cf = csv.DictReader(f)
            for row in cf:
                if row['event'] == "[Execute]":
                    self.assertAlmostEqual(float(row['w-percent']), 1.0)
                    if hasattr(self, "_execute_count"):
                        self.assertEqual(int(row['count']), self._execute_count)


if __name__ == '__main__':
    unittest.main()
