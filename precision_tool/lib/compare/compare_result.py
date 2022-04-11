import collections
import os
import numpy as np
from ..util.util import util
from ..util.constant import Constant
from ..util.precision_tool_exception import PrecisionToolException
from ..util.precision_tool_exception import catch_tool_exception


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
    def __init__(self, item=None):
        self.index = 0
        self.left = 1
        self.right = 2
        self.tensor_index = 3
        self.cosine_similarity = 4
        self.max_abs = 5
        if item is not None:
            self.update(item)

    def update(self, item):
        for i, value in enumerate(item):
            self.left = i if value == 'LeftOp' else self.left
            self.right = i if value == 'RightOp' else self.right
            self.tensor_index = i if value == 'TensorIndex' else self.tensor_index
            self.cosine_similarity = i if value == 'CosineSimilarity' else self.cosine_similarity
            self.max_abs = i if value == 'MaxAbsoluteError' else self.max_abs


class CompareItem(object):
    def __init__(self, op_name, item, row_map):
        self.row_map = row_map
        self.index = int(item[self.row_map.index])
        self.op_name = op_name
        self.left = item[self.row_map.left].split(" ")
        self.right = item[self.row_map.right].split(" ")
        self.input = []
        self.output = []

    def update(self, item):
        tensor_index = item[self.row_map.tensor_index]
        if tensor_index not in ['NaN', '*']:
            item_detail = tensor_index.split(':')
            if len(item_detail) != 3:
                raise PrecisionToolException("item:%d tensor index invalid. [%s]" % (
                    item[self.row_map.index], tensor_index))
            if item_detail[1] == 'input':
                self.input.insert(int(item_detail[2]), item)
            else:
                self.output.insert(int(item_detail[2]), item)

    def is_cosine_sim_over_threshold(self, threshold):
        for item in self.output:
            if item[self.row_map.cosine_similarity] == 'NaN':
                continue
            if float(item[self.row_map.cosine_similarity]) <= threshold:
                return True
        return False

    @staticmethod
    def _color_data(data, threshold):
        try:
            data = float(data)
            if np.isnan(data):
                raise ValueError
            elif data <= threshold:
                return "[red]%s[/red]" % data
            else:
                return "[green]%s[/green]" % data
        except ValueError:
            return "[yellow]%s[/yellow]" % data

    def summary(self, threshold):
        content = ["Left:  %s" % self.left, "Right: %s" % self.right, "Input: "]
        input_txt = []
        for i, item in enumerate(self.input):
            input_txt.append(" - [%d]%s" % (i, self._color_data(item[self.row_map.cosine_similarity], threshold)))
        content.extend([Constant.TAB_LINE.join(input_txt), "Output:"])
        output_txt = []
        for i, item in enumerate(self.output):
            output_txt.append(" - [%d]%s" % (i, self._color_data(item[self.row_map.cosine_similarity], threshold)))
        content.append(Constant.TAB_LINE.join(output_txt))
        title = "[%d] %s" % (self.index, self.op_name)
        util.print_panel(Constant.NEW_LINE.join(content), title=title)


class CompareResult(object):
    def __init__(self, file_path):
        self.file_path = file_path
        self.ops = None
        self.prepare()

    @catch_tool_exception
    def prepare(self):
        if not str(self.file_path).endswith(Constant.Suffix.CSV):
            raise PrecisionToolException("Compare result file %s not a csv file." % self.file_path)
        if not os.path.isfile(self.file_path):
            raise PrecisionToolException("Compare result file %s not exist." % self.file_path)
        items = util.read_csv(self.file_path)
        self.ops = collections.OrderedDict()
        row_map = RowMap()
        for item in items:
            if item[row_map.index] == 'Index':
                row_map.update(item)
                continue
            if item[row_map.tensor_index] in ['NaN', '*']:
                continue
            tensor_index = item[row_map.tensor_index]
            op_name = tensor_index.split(":")[0]
            if op_name not in self.ops:
                self.ops[op_name] = CompareItem(op_name, item, row_map)
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
