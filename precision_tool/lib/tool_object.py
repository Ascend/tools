# coding=utf-8


class ToolObject(object):
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ToolObject, cls).__new__(cls, *args, **kwargs)
        return cls._instance
