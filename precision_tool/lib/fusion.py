import json
import os
import shutil

from lib.tool_object import ToolObject
from lib.util import util
from lib.util import LOG
import config as cfg
from rich.table import Table
from rich.columns import Columns
from rich import print

FUSION_RESULT_FILE_NAME = 'fusion_result.json'


class FusionResult(object):
    def __init__(self, fusion_json):
        self.fusion_json = fusion_json

    @staticmethod
    def _get_effect_fusion(fusion):
        res = {}
        for fusion_name in fusion:
            effect_times = int(fusion[fusion_name]['effect_times'])
            if effect_times > 0:
                res[fusion_name] = effect_times
        return res

    def get_effect_graph_fusion(self):
        return self._get_effect_fusion(self.fusion_json['graph_fusion'])

    def get_effect_ub_fusion(self):
        return self._get_effect_fusion(self.fusion_json['ub_fusion'])

    def graph_id(self):
        return self.fusion_json['graphId']


class Fusion(ToolObject):
    fusion_result = []

    def __init__(self):
        super(Fusion, self).__init__()

    def prepare(self, json_path='./'):
        util.create_dir(cfg.FUSION_DIR)
        file_path = os.path.join(json_path, FUSION_RESULT_FILE_NAME)
        file_path_local = os.path.join(cfg.FUSION_DIR, FUSION_RESULT_FILE_NAME)
        if not os.path.isfile(file_path):
            if not os.path.isfile(file_path_local):
                LOG.warning("Can not find fusion result json.")
                return
        else:
            shutil.copy(file_path, cfg.FUSION_DIR)
        fe_jsons = self._get_result_jsons(file_path_local)
        for fe_json in fe_jsons:
            self.fusion_result.append(FusionResult(fe_json))

    def _get_result_jsons(self, file_name):
        result_jsons = []
        with open(file_name, 'r') as f:
            txt = f.read()
            sk = []
            start = -1
            for i in range(len(txt)):
                if txt[i] == '{':
                    sk.append('{')
                if txt[i] == '}':
                    sk.pop()
                if len(sk) == 0:
                    result_jsons.append(json.loads(txt[start+1: i+1]))
                    start = i
        return result_jsons

    @staticmethod
    def _build_table(title, fusion):
        table = Table(title=title)
        table.add_column('Fusion Name')
        table.add_column('Effect times')
        for f in fusion:
            table.add_row(f, str(fusion[f]))
        return table

    def summary(self):
        LOG.info("<====== Effect Fusion List ======>")
        for fusion in self.fusion_result:
            graph_fusion_table = self._build_table('Graph Fusion [GraphID: %s]' % fusion.graph_id(),
                                                   fusion.get_effect_graph_fusion())
            ub_fusion_table = self._build_table('UB Fusion [GraphID: %s]' % fusion.graph_id(),
                                                fusion.get_effect_ub_fusion())
            util.print_panel(Columns([graph_fusion_table, ub_fusion_table]), title='GraphID:' + fusion.graph_id(),
                             fit=True)
        LOG.info("<====== Effect Fusion List ======>")
