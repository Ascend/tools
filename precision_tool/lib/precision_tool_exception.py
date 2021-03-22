

PRECISION_ERROR_INVALID_FILE = 1


class PrecisionToolException(Exception):
    """
    Class for PrecisionTool Exception
    """
    def __init__(self, error_info):
        super(PrecisionToolException, self).__init__()
        self.error_info = error_info
