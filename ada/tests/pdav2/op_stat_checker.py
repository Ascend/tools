import unittest
import os
import csv


class OpStatChecker(unittest.TestCase):
    def init(self, path):
        self.records = []
        self.assertTrue(os.path.isfile(path))
        with open(path, 'r') as f:
            cf = csv.DictReader(f)
            for row in cf:
                self.records.append(row)
        return self

    def FindRecords(self, name, event):
        records = []
        for rec in self.records:
            if rec['name'] == name and rec['event'] == event:
                records.append(rec)
        return records


if __name__ == '__main__':
    unittest.main()
