from collections import defaultdict
import os
import inspect


_reporters = {}
_categories_to_reporter_names = defaultdict(list)
_files_to_reporter_names = defaultdict(list)


def get_all_reporter_names():
    return _reporters.keys()


def get_all_reporter_categories():
    categories = set(_categories_to_reporter_names.keys())
    categories.remove("basic")
    return categories


def get_names_by_category(category):
    return _categories_to_reporter_names.get(category, [])


def get_reporter(name):
    return _reporters[name]


def reporter(name, category=None):
    def register_reporter(cls):
        if name in _reporters:
            return
        _reporters[name] = cls
        if category is None:
            _categories_to_reporter_names["basic"].append(name)
        else:
            _categories_to_reporter_names[category].append(name)
        _files_to_reporter_names[os.path.realpath(inspect.getfile(cls))].append(name)
        return cls
    return register_reporter
