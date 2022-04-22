import os
import shutil


def get_test_root_path():
    self_path = os.path.abspath(__file__)
    return os.path.dirname(self_path)


def get_temp_path():
    return os.path.join(get_test_root_path(), 'temp-output')


def get_test_path(name):
    return os.path.join(get_temp_path(), name)


def create_test_path(name):
    test_path = get_test_path(name)
    if not os.path.isdir(test_path):
        os.mkdir(test_path)
    return test_path


def clear_test_path(name):
    test_path = get_test_path(name)
    if os.path.isdir(test_path):
        shutil.rmtree(test_path)


def copy_all_files_to(from_path, to_path):
    if os.path.isdir(to_path):
        shutil.rmtree(to_path)
    shutil.copytree(from_path, to_path)
