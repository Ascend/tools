import collections
import os
from lib.util import util
from lib.precision_tool_exception import PrecisionToolException
from lib.precision_tool_exception import catch_tool_exception

NEW_LINE = "\n"


class RowMap(object):
    """
    'Index': 0,
    'LeftOp': 1,
    'RightOp': 2,
    'TensorIdx': 3,    # TensorIndex
    'CosSim': 4,    # CosineSimilarity
    'MaxAbs': 5,   # MaxAbsoluteError
    'ARE': 6,   # AccumulatedRelativeError
    'RED': 7,   # RelativeEuclideanDistance
    'KLD': 8,   # KullbackLeiblerDivergence
    'StandardDeviation': 9     # StandardDeviation
    """
    index = 0
    left = 1
    right = 2
    tensor_index = 3
    cosine_similarity = 4
    max_abs = 5


class CompareItem(object):
    def __init__(self, op_name, item):
        self.index = int(item[RowMap.index])
        self.op_name = op_name
        self.left = item[RowMap.left].split(" ")
        self.right = item[RowMap.right].split(" ")
        self.input = []
        self.output = []

    def update(self, item):
        tensor_index = item[RowMap.tensor_index]
        if tensor_index not in ['NaN', '*']:
            item_detail = tensor_index.split(':')
            if len(item_detail) != 3:
                raise PrecisionToolException("item:%d tensor index invalid. [%s]" % (item[RowMap.index], tensor_index))
            if item_detail[1] == 'input':
                self.input.insert(int(item_detail[2]), item)
            else:
                self.output.insert(int(item_detail[2]), item)

    def is_cosine_sim_over_threshold(self, threshold):
        for item in self.output:
            if item[RowMap.cosine_similarity] == 'NaN':
                continue
            if float(item[RowMap.cosine_similarity]) <= threshold:
                return True
        return False

    def summary(self):
        content = ["Left:  %s" % self.left, "Right: %s" % self.right, "Input:"]
        for i, item in enumerate(self.input):
            content.append("  - [%d]%s" % (i, item[RowMap.cosine_similarity]))
        content.append("Output:")
        for i, item in enumerate(self.output):
            content.append("  - [%d]%s" % (i, item[RowMap.cosine_similarity]))
        title = "[%d] %s" % (self.index, self.op_name)
        util.print_panel(NEW_LINE.join(content), title=title)


class CompareResult(object):
    def __init__(self, file_path):
        self.file_path = file_path
        self.ops = None
        self.prepare()

    @catch_tool_exception
    def prepare(self):
        if not os.path.isfile(self.file_path):
            raise PrecisionToolException("Compare result file %s not exist" % self.file_path)
        items = util.read_csv(self.file_path)
        self.ops = collections.OrderedDict()
        for item in items:
            if item[RowMap.index] == 'Index' or item[RowMap.tensor_index] in ['NaN', '*']:
                continue
            tensor_index = item[RowMap.tensor_index]
            op_name = tensor_index.split(":")[0]
            if op_name not in self.ops:
                self.ops[op_name] = CompareItem(op_name, item)
            op = self.ops[op_name]
            op.update(item)

    def get_compare_item_by_op(self, op_name):
        if self.ops is None:
            self.prepare()
        if self.ops is None:
            raise PrecisionToolException("Invalid compare result file: %s" % self.file_path)
        if op_name in self.ops:
            return self.ops[op_name]
        return None

    def get_op_by_cosine_sim_threshold(self, threshold, limit=-1):
        result = []
        for compare_item in self.ops.values():
            if compare_item.is_cosine_sim_over_threshold(threshold):
                result.append(compare_item)
                if len(result) == limit:
                    break
        return result
