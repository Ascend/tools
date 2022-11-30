from enum import Enum


class Arg(object):
    def __init__(self, msame_arg, atc_arg, msquickcmp_arg):
        self.atc_arg = atc_arg
        self.msame_arg = msame_arg
        self.msquickcmp_arg = msquickcmp_arg


class DynamicArgumentEnum(Enum):
    # enum struct Arg(msame_arg, atc_arg, msquickcmp_arg)
    DYM_BATCH = Arg("--dymBatch", "--dynamic_batch_size", None)
    DYM_SHAPE = Arg("--dymShape", "--input_shape_range", "input_shape")
    DYM_DIMS = Arg("--dymDims", "--dynamic_dims", "input_shape")

    @staticmethod
    def get_all_args() -> list:
        """
        get all argument enum, return as a list
        """
        return list(map(lambda arg: arg, DynamicArgumentEnum))
