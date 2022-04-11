# coding=utf-8
import os
import time
import pathlib
import shutil
from ..util.util import util
from ..util.constant import Constant
from ..config import config as cfg
from ..util.precision_tool_exception import PrecisionToolException


class MsQuickCmpAdapter(object):
    def __init__(self, output_path):
        self.output_path = output_path
        self.log = util.get_log()

    def run(self):
        if self.output_path is None or not os.path.isdir(self.output_path):
            raise PrecisionToolException("Invalid output path.")
        if os.path.exists(cfg.DATA_ROOT_DIR):
            raise PrecisionToolException("Precision data dir exist, can not adapt msquickcmp result.")

        for dir_path, dir_names, file_names in os.walk(self.output_path, followlinks=True):
            if 'model' in dir_names:
                self._adapt_model(os.path.join(dir_path, 'model'))
            if 'dump_data' in dir_names:
                self._adapt_dump(os.path.join(dir_path, 'dump_data'))
            for file_name in file_names:
                if str(file_name).endswith(Constant.Suffix.CSV):
                    self._adapt_vector_compare_result(os.path.join(dir_path, file_name))

    def _adapt_model(self, path):
        file_names = os.listdir(path)
        graph_id = 0
        for file_name in file_names:
            if str(file_name).endswith(Constant.Suffix.JSON):
                self.log.info("Find msquickcmp model json: %s", file_name)
                util.create_dir(cfg.DEFAULT_NPU_GRAPH_DIR)
                graph_file_name = 'ge_proto_%d_%s.txt' % (graph_id, cfg.BUILD_JSON_GRAPH_NAME)
                graph_json_file_name = graph_file_name + Constant.Suffix.JSON
                pathlib.Path(os.path.join(cfg.DEFAULT_NPU_GRAPH_DIR, graph_file_name)).touch()
                src_path = os.path.join(path, file_name)
                dst_path = os.path.join(cfg.DEFAULT_NPU_GRAPH_DIR, graph_json_file_name)
                self.log.info("Copy graph file: %s->%s", src_path, dst_path)
                shutil.copy(src_path, dst_path)
                time.sleep(3)
                pathlib.Path(dst_path).touch()
        if not util.empty_dir(cfg.DEFAULT_NPU_GRAPH_DIR):
            self.log.info("Adapt model success.")

    def _adapt_dump(self, path):
        dir_names = os.listdir(path)
        if 'tf' in dir_names:
            self._adapt_tf_dump(os.path.join(path, 'tf'))
        if 'onnx' in dir_names:
            self._adapt_tf_dump(os.path.join(path, 'onnx'))
        if 'npu' in dir_names:
            self._adapt_npu_dump(os.path.join(path, 'npu'))

    def _adapt_tf_dump(self, path):
        if util.empty_dir(path):
            return
        src_path = os.path.abspath(path)
        util.create_dir(cfg.TF_DIR)
        dst_path = cfg.TF_DUMP_DIR
        self.log.info("Create symbol link file: %s->%s", src_path, dst_path)
        os.symlink(src_path, dst_path)
        self.log.info("Adapt tf dump success.")

    def _adapt_npu_dump(self, path):
        sub_dirs = os.listdir(path)
        self.log.info("Find npu dump dir:%s", sub_dirs)
        sub_dirs = filter(lambda x: str(x).isdigit(), sub_dirs)
        for sub_dir in sub_dirs:
            util.create_dir(cfg.DEFAULT_NPU_DUMP_DIR)
            src_path = os.path.abspath(os.path.join(path, sub_dir))
            dst_path = os.path.join(cfg.DEFAULT_NPU_DUMP_DIR, sub_dir)
            self.log.info("Create symbol link file: %s->%s", src_path, dst_path)
            os.symlink(src_path, dst_path)
            self.log.info("Adapt npu dump success.")

    def _adapt_vector_compare_result(self, path):
        target_path = os.path.join(cfg.VECTOR_COMPARE_PATH, '0')
        util.create_dir(target_path)
        dst_path = os.path.join(target_path, os.path.basename(path))
        shutil.copy(path, dst_path)
        self.log.info("Adapt vector compare result.")
