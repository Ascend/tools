# coding=utf-8
import logging


class PrecisionToolException(Exception):
    """
    Class for PrecisionTool Exception
    """
    def __init__(self, error_info):
        super(PrecisionToolException, self).__init__()
        self.error_info = error_info


def catch_tool_exception(fuc):
    def handle(*args, **kwargs):
        try:
            return fuc(*args, **kwargs)
        except PrecisionToolException as pte:
            log = logging.getLogger()
            log.warning(pte.error_info)
    return handle
