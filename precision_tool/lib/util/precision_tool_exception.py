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
        log = logging.getLogger()
        try:
            return fuc(*args, **kwargs)
        except PrecisionToolException as pte:
            log.warning(pte.error_info)
        except SystemExit:
            # do not exit
            log.debug("Exit")
    return handle
