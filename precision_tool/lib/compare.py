# coding=utf-8
"""
Compare
"""
import os
import numpy as np
from lib.tool_object import ToolObject
from lib.graph import Graph
from lib.dump import Dump
from lib.util import util
from lib.util import LOG
from rich.table import Table
from rich import print as rich_print
from rich.columns import Columns
import config as cfg

graph = Graph()
dump = Dump()

ROW_MAP = {
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
}


class Compare(ToolObject):
    """
    """
    vector_compare_result = None

    def __init__(self):
        """__init__"""
        super(Compare, self).__init__()

    def vector_compare(self):
        """ compare all ops """
        if util.empty_dir(cfg.DUMP_FILES_CPU):
            LOG.warning("No valid dump file in %s" % cfg.DUMP_FILES_CPU)
            return
        LOG.info("[VectorCompare] Running...")
        util.clear_dir(cfg.VECTOR_COMPARE_PATH)
        count = 0
        for graph_name in graph.sub_graph_json_map:
            graph_json = graph.sub_graph_json_map[graph_name]
            for dump_dir in dump.npu_parent_dirs:
                if graph_name not in dump_dir:
                    continue
                count += 1
                util.compare_vector(dump_dir, cfg.DUMP_FILES_CPU, graph_json, cfg.VECTOR_COMPARE_PATH)
        LOG.info("[VectorCompare] Done. Process [%d] graphs." % count)
        self._parse_result_files()
        self.vector_summary()

    def vector_summary(self):
        """ Print not NaN result """
        for file_name in self.vector_compare_result:
            items = self.vector_compare_result[file_name]
            table = self._create_table(file_name, ROW_MAP.keys()[3:])
            for item in items:
                if len(item) == 0 or item[ROW_MAP['TensorIdx']] == 'TensorIndex' or item[ROW_MAP['MaxAbs']] == 'NaN':
                    continue
                # valid data
                table.add_row(item[ROW_MAP['TensorIdx']], item[ROW_MAP['CosSim']], item[ROW_MAP['MaxAbs']],
                              item[ROW_MAP['ARE']], item[ROW_MAP['RED']], item[ROW_MAP['KLD']],
                              item[ROW_MAP['StandardDeviation']])

            rich_print("[CosSim: CosineSimilarity] [MaxAbs: MaxAbsoluteError] [ARE: MaxAbsoluteError] "
                       "[RED: RelativeEuclideanDistance] [KLD: KullbackLeiblerDivergence]")
            rich_print(table)

    def _parse_result_files(self):
        result_files = util.list_vector_compare_result_files(cfg.VECTOR_COMPARE_PATH)
        self.vector_compare_result = {}
        for file in result_files.values():
            self.vector_compare_result[file['file_name']] = util.read_csv(file['path'])

    @staticmethod
    def _detect_file(file_name):
        if os.path.isfile(file_name):
            return file_name
        for parent_dir in [cfg.DUMP_FILES_DECODE, cfg.DUMP_FILES_CPU, cfg.DUMP_FILES_OVERFLOW_DECODE]:
            if os.path.isfile(os.path.join(parent_dir, file_name)):
                return os.path.join(parent_dir, file_name)
        return None

    @staticmethod
    def _create_table(title, columns):
        table = Table(title=title)
        for column_name in columns:
            table.add_column(column_name, overflow='fold')
        return table

    def compare_data(self, left, right, rl=0.001, al=0.001, print_n=20):
        """Compare data"""
        left = self._detect_file(left)
        right = self._detect_file(right)
        if left is None or right is None:
            LOG.error("invalid input or output")
            return
        # save to txt
        util.save_npy_to_txt(left)
        util.save_npy_to_txt(right)

        data_left = np.load(left).astype(np.float32)
        data_right = np.load(right).astype(np.float32)
        shape_left = data_left.shape
        shape_right = data_right.shape
        if shape_left != shape_right:
            LOG.warning("Data shape not equal: %s vs %s" % (data_left.shape, data_right.shape))
        data_left = data_left.reshape(-1)
        data_right = data_right.reshape(-1)
        if data_left.shape[0] != data_right.shape[0]:
            LOG.warning("Data size not equal: %s vs %s" % (data_left.shape, data_right.shape))
        all_close = np.allclose(data_left, data_right, atol=al, rtol=rl)
        # cos_sim = 1 - spatial.distance.cosine(data_left, data_right)
        cos_sim = np.dot(data_left, data_right) / (
                np.sqrt(np.dot(data_left, data_left)) * np.sqrt(np.dot(data_right, data_right)))
        err_cnt = 0
        total_cnt = data_left.shape[0]
        diff_table_columns = ['Index', 'Left', 'Right', 'Diff']
        err_table = self._create_table("Error Item Table", diff_table_columns)
        top_table = self._create_table("Top Item Table", diff_table_columns)
        for i in range(total_cnt):
            abs_diff = abs(data_left[i] - data_right[i])
            if abs_diff > (al + rl * abs(data_right[i])):
                if i < print_n:
                    top_table.add_row(str(i), str(data_left[i]), str(data_right[i]), str(abs_diff))
                if err_cnt < print_n:
                    err_table.add_row(str(i), str(data_left[i]), str(data_right[i]), str(abs_diff))
                err_cnt += 1
        err_percent = float(err_cnt / total_cnt)
        rich_print(Columns([err_table, top_table]))
        content = 'SrcFile: %s \nDstFile: %s\nSrcFile: %s.txt\nDstFile: %s.txt' % (left, right, left, right)
        content += '\nNumCnt:  %s\nAllClose: %s\nCosSim:   %s\nErrorPer: %s (rl= %s, al= %s)' % (
            total_cnt, all_close, cos_sim, err_percent, rl, al)
        util.print_panel(content)

    def check_op(self, op_name, op_type):
        """
        use dump data to check op precision
        :param op_name:
        :param op_type:
        :return:
        """