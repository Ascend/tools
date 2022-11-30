import unittest
from ada import reporter_registry
from ada.reporter_registry import reporter


@reporter("Test1")
class TestReporter1:
    def __init__(self, pds):
        self._pds = pds

    def report(self, path):
        return "pds: {}".format(self._pds)


@reporter("Test2")
class TestReporter2:
    pass


@reporter("c1t1", category="c1")
class C1TestReporter1:
    pass


@reporter("c1t2", category="c1")
class C1TestReporter2:
    pass


@reporter("c1t2")
class C1TestReporter2Dup:
    pass


class ReporterRegistryTestCase(unittest.TestCase):
    def test_register_reporter_success(self):
        self.assertIsNotNone(reporter_registry.get_reporter("Test1"))
        self.assertIsNotNone(reporter_registry.get_reporter("Test2"))
        self.assertIsNotNone(reporter_registry.get_reporter("c1t1"))
        self.assertIsNotNone(reporter_registry.get_reporter("c1t2"))

    def test_register_category_success(self):
        self.assertEqual(reporter_registry.get_names_by_category('c1'), ["c1t1", "c1t2"])

    def test_not_register_category(self):
        self.assertEqual(reporter_registry.get_names_by_category('c2'), [])

    def test_reporter_init_success(self):
        reporter_builder = reporter_registry.get_reporter("Test1")
        self.assertIsNotNone(reporter_builder)
        r = reporter_builder("test1")
        self.assertEqual(r.report(), "pds: test1")

    def test_register_builtin_reporter_success(self):
        from ada.pdav2 import load_all_builtin_reporters
        load_all_builtin_reporters()
        self.assertIsNotNone(reporter_registry.get_reporter("summary"))
        self.assertIsNotNone(reporter_registry.get_reporter("opstat"))
        self.assertIsNotNone(reporter_registry.get_reporter("trace"))


if __name__ == '__main__':
    unittest.main()
