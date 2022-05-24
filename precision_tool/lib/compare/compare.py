# coding=utf-8
"""
Compare
"""
import json
import os
import numpy as np
from .compare_result import CompareResult
from ..util.constant import Constant
from ..util.util import util
from ..config import config as cfg
from ..util.precision_tool_exception import PrecisionToolException
from ..util.precision_tool_exception import catch_tool_exception


class Compare(object):
    def __init__(self):
        """Init"""
        super(Compare, self).__init__()
        self.log = util.get_log()
        self.vector_compare_results = {}

    @catch_tool_exception
    def prepare(self):
        util.create_dir(cfg.VECTOR_COMPARE_PATH)

    def npu_tf_vector_compare(self, graphs, npu_root_dir, tf_root_dir, result_dir):
        """Compare npu dump data with tf dump data
        :param graphs: npu ge graph json file list
        :param npu_root_dir:
        :param tf_root_dir:
        :param result_dir: result dir
        :return:
        """
        for graph_file in graphs:
            self.log.info("Compare npu tf with graph %s", graph_file)
            sub_graphs = self._get_sub_graphs(graph_file)
            if sub_graphs is None:
                continue
            for sub_graph in sub_graphs:
                npu_dir = self._get_sub_dir_by_sub_graph_name(sub_graph, npu_root_dir)

                if npu_dir is None:
                    self.log.warning("Can not find any sub graph dir named %s", npu_dir)
                    # for some infer case, sub_graph name may not match sub dir name.
                    npu_dir_0 = self._get_sub_dir_by_sub_graph_name(sub_graph + '_0', npu_root_dir)
                    if npu_dir_0 is None:
                        self.log.warning("Can not find any sub graph dir named %s", npu_dir_0)
                        continue
                    npu_dir = npu_dir_0
                self.vector_compare(npu_dir, tf_root_dir, result_dir, graph_file)

    @catch_tool_exception
    def _get_sub_dir_by_sub_graph_name(self, sub_graph, npu_root_dir):
        sub_graph_dirs = []
        for dir_path, dir_names, file_names in os.walk(npu_root_dir, followlinks=True):
            if sub_graph in dir_names:
                # walk sub graph dir
                for sub_dir_path, sub_dir_names, sub_file_names in os.walk(os.path.join(dir_path, sub_graph),
                                                                           followlinks=True):
                    if len(sub_dir_names) == 0:
                        sub_graph_dirs.append(sub_dir_path)
        if len(sub_graph_dirs) == 0:
            return None
        self.log.warning("Find [%d] dirs in sub graph dir [%s], %s, compare first.", len(sub_graph_dirs), sub_graph,
                         sub_graph_dirs)
        return sub_graph_dirs[0]

    @catch_tool_exception
    def _get_sub_graphs(self, graph_file):
        with open(graph_file, 'r') as f:
            graph_json = json.load(f)
            if 'graph' not in graph_json:
                raise PrecisionToolException("No graph in file: %s" % graph_file)
            sub_graphs = []
            for graph in graph_json['graph']:
                sub_graphs.append(graph['name'])
        return sub_graphs

    '''
    @staticmethod
    def _get_ge_default_dirs(self, root_dir):
        for dir_path, dir_names, file_names in os.walk(root_dir, followlinks=True):
            for dir_name in dir_names:
    '''

    def npu_vector_compare(self, debug_0_root_dir, debug_1_root_dir):
        """Compare two npu dump data
        :param debug_0_root_dir:
        :param debug_1_root_dir:
        :return:
        """
        # debug_0_sub_dirs = self._get_ge_default_dirs(debug_0_root_dir)
        # debug_1_sub_dirs = self._get_ge_default_dirs(debug_1_root_dir)

    def vector_compare(self, lh_path, rh_path, result_dir, graph_json=None):
        """Compare all ops"""
        if lh_path is None or util.empty_dir(lh_path):
            raise PrecisionToolException("No valid dump file in %s" % lh_path)
        if rh_path is None or util.empty_dir(rh_path):
            raise PrecisionToolException("No valid dump file in %s" % rh_path)
        self.log.info("Start vector compare process...")
        util.compare_vector(lh_path, rh_path, graph_json, result_dir)
        self.log.info("Vector compare process finish.")

    def _get_compare_result_by_file_name(self, file_name):
        results = []
        if file_name is None:
            sub_dir = util.get_newest_dir(cfg.VECTOR_COMPARE_PATH)
            if sub_dir == '':
                raise PrecisionToolException("Empty vector compare path:%s" % cfg.VECTOR_COMPARE_PATH)
            file_name = os.path.join(cfg.VECTOR_COMPARE_PATH, sub_dir)
        if os.path.isfile(file_name):
            results.append(CompareResult(file_name))
        if os.path.isdir(file_name):
            vector_compare_result_files = util.list_vector_compare_result_files(file_name)
            if vector_compare_result_files is None or len(vector_compare_result_files) == 0:
                raise PrecisionToolException("Can not find any vector compare result in dir:%s" % file_name)
            file_list = sorted(vector_compare_result_files.values(), key=lambda x: x.timestamp)
            file_names = [x.file_name for x in file_list]
            self.log.debug("Find %s result files in dir %s", file_names, file_name)
            for file in file_list:
                results.append(CompareResult(file.path))
        return results

    @catch_tool_exception
    def vector_summary(self, file_name=None, cos_sim_threshold=0.98, limit=1):
        """Print not NaN result in vector compare result"""
        compare_results = self._get_compare_result_by_file_name(file_name)
        error_ops = []
        for compare_result in compare_results:
            err_ops = compare_result.get_op_by_cosine_sim_threshold(cos_sim_threshold, limit)
            self.log.info("Find %d ops less then %s in %s", len(err_ops), cos_sim_threshold, compare_result.file_path)
            error_ops.extend(err_ops)
        if len(error_ops) == 0:
            self.log.info("Can not find any compare result over threshold: %s" % cos_sim_threshold)
        else:
            for i, error_op in enumerate(error_ops):
                if i < limit:
                    error_op.summary(cos_sim_threshold)
        return error_ops

    def compare_data(self, left, right, save_txt=False, rl=0.001, al=0.001, diff_count=20):
        """Compare data"""
        left = self._detect_file(left)
        right = self._detect_file(right)
        if left is None or right is None:
            raise PrecisionToolException("invalid input or output")
        # save to txt
        if save_txt:
            util.save_npy_to_txt(left)
            util.save_npy_to_txt(right)
        # compare data
        total_cnt, all_close, cos_sim, err_percent = self._do_compare_data(left, right, rl, al, diff_count)
        content = ['Left:', ' ├─ NpyFile: %s' % left]
        if save_txt:
            content.append(' ├─ TxtFile: [green]%s.txt[/green]' % left)
        content.append(' └─ NpySpec: [yellow]%s[/yellow]' % util.gen_npy_info_txt(left))
        content.append('Right:')
        content.append(' ├─ NpyFile: %s' % right)
        if save_txt:
            content.append(' ├─ TxtFile: [green]%s.txt[/green]' % right)
        content.append(' └─ NpySpec: [yellow]%s[/yellow]' % util.gen_npy_info_txt(right))
        content.append('NumCnt:   %s' % total_cnt)
        content.append('AllClose: %s' % all_close)
        content.append('CosSim:   %s' % cos_sim)
        content.append('ErrorPer: %s  (rl= %s, al= %s)' % (err_percent, rl, al))
        util.print_panel(Constant.NEW_LINE.join(content))

    def _do_compare_data(self, left, right, rl=0.001, al=0.001, diff_count=20):
        data_left = np.load(left).astype(np.float32)
        data_right = np.load(right).astype(np.float32)
        shape_left = data_left.shape
        shape_right = data_right.shape
        if shape_left != shape_right:
            self.log.warning("Data shape not equal: %s vs %s", data_left.shape, data_right.shape)
        data_left = data_left.reshape(-1)
        data_right = data_right.reshape(-1)
        if data_left.shape[0] != data_right.shape[0]:
            self.log.warning("Data size not equal: %s vs %s", data_left.shape, data_right.shape)
            if data_left.shape[0] < data_right.shape[0]:
                data_left = np.pad(data_left, (0, data_right.shape[0] - data_left.shape[0]), 'constant')
            else:
                data_right = np.pad(data_right,(0, data_left.shape[0] - data_right.shape[0]), 'constant')
        all_close = np.allclose(data_left, data_right, atol=al, rtol=rl)
        # cos_sim = 1 - spatial.distance.cosine(data_left, data_right)
        cos_sim = np.dot(data_left, data_right) / (
                np.sqrt(np.dot(data_left, data_left)) * np.sqrt(np.dot(data_right, data_right)))
        err_cnt = 0
        total_cnt = data_left.shape[0]
        diff_table_columns = ['Index', 'Left', 'Right', 'Diff']
        err_table = util.create_table("Error Item Table", diff_table_columns)
        top_table = util.create_table("Top Item Table", diff_table_columns)
        for i in range(total_cnt):
            abs_diff = abs(data_left[i] - data_right[i])
            if i < diff_count:
                top_table.add_row(str(i), str(data_left[i]), str(data_right[i]), str(abs_diff))
            if abs_diff > (al + rl * abs(data_right[i])):
                if err_cnt < diff_count:
                    err_table.add_row(str(i), str(data_left[i]), str(data_right[i]), str(abs_diff))
                err_cnt += 1
        err_percent = float(err_cnt / total_cnt)
        util.print(util.create_columns([err_table, top_table]))
        return total_cnt, all_close, cos_sim, err_percent

    def _detect_file(self, file_name):
        """Find files in npu/overflow/cpu dump dir"""
        if os.path.isfile(file_name):
            return file_name
        for parent_dir in [cfg.TMP_DIR, cfg.TF_DUMP_DIR]:
            file_infos = util.list_numpy_files(parent_dir, file_name)
            if len(file_infos) > 0:
                self.log.info("Find %s, choose first one.", list(file_infos.keys()))
                return list(file_infos.values())[0].path
        return None
