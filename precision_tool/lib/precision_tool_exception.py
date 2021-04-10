# coding=utf-8

class PrecisionToolException(Exception):
    """
    Class for PrecisionTool Exception
    """
    def __init__(self, error_info):
        super(PrecisionToolException, self).__init__()
        self.error_info = error_info
