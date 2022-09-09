import json
import os

import numpy as np

from frontend.utils import logger


class ListInfo(object):
    def __init__(self):
        self.min = 0.0
        self.max = 0.0
        self.mean = 0.0
        self.median = 0.0
        self.percentile = 0.0


class Summary(object):
    def __init__(self):
        self.reset()
        self.infodict = { "filesinfo" : {} }

    def reset(self):
        self.h2d_latency_list = []
        self.d2h_latency_list = []
        self.npu_compute_time_list = []

    @staticmethod
    def get_list_info(work_list, percentile_scale):
        list_info = ListInfo()
        if len(work_list) != 0:
            list_info.min = np.min(work_list)
            list_info.max = np.max(work_list)
            list_info.mean = np.mean(work_list)
            list_info.median = np.median(work_list)
            list_info.percentile = np.percentile(work_list, percentile_scale)

        return list_info

    def add_sample_id_infiles(self, sample_id, infiles):
        if self.infodict["filesinfo"].get(sample_id) == None:
            self.infodict["filesinfo"][sample_id] = {"infiles": [], "outfiles":[] }
        if len(self.infodict["filesinfo"][sample_id]["infiles"]) == 0:
            for files in infiles:
                self.infodict["filesinfo"][sample_id]["infiles"].append(files)
    def append_sample_id_outfile(self, sample_id, outfile):
        if self.infodict["filesinfo"].get(sample_id) == None:
            self.infodict["filesinfo"][sample_id] = {"infiles": [], "outfiles":[] }
        self.infodict["filesinfo"][sample_id]["outfiles"].append(outfile)

    def add_args(self, args):
        self.infodict["args"] = args

    def report(self, batchsize, output_prefix):
        scale = 99

        npu_compute_time = Summary.get_list_info(self.npu_compute_time_list, scale)
        h2d_latency = Summary.get_list_info(self.h2d_latency_list, scale)
        d2h_latency = Summary.get_list_info(self.d2h_latency_list, scale)
        if npu_compute_time.mean == 0:
            throughput = 0
        else:
            throughput = 1000*batchsize/npu_compute_time.mean

        self.infodict['NPU_compute_time'] = {"min": npu_compute_time.min, "max": npu_compute_time.max, "mean": npu_compute_time.mean,
                                    "median": npu_compute_time.median, "percentile({}%)".format(scale): npu_compute_time.percentile}
        self.infodict['H2D_latency'] = {"min": h2d_latency.min, "max": h2d_latency.max, "mean": h2d_latency.mean,
                               "median": h2d_latency.median, "percentile({}%)".format(scale): h2d_latency.percentile}
        self.infodict['D2H_latency'] = {"min": d2h_latency.min, "max": d2h_latency.max, "mean": d2h_latency.mean,
                               "median": d2h_latency.median, "percentile({}%)".format(scale): d2h_latency.percentile}
        self.infodict['throughput'] = throughput

        #logger.debug("infer finish (ms) sumary:{}".format(self.infodict))
        logger.info("-----------------Performance Summary------------------")
        logger.info("H2D_latency (ms): min = {0}, max = {1}, mean = {2}, median = {3}, percentile({4}%) = {5}"
                    .format(h2d_latency.min, h2d_latency.max, h2d_latency.mean, h2d_latency.median, scale,
                            h2d_latency.percentile))
        logger.info("NPU_compute_time (ms): min = {0}, max = {1}, mean = {2}, median = {3}, percentile({4}%) = {5}"
                    .format(npu_compute_time.min, npu_compute_time.max, npu_compute_time.mean, npu_compute_time.median,
                            scale, npu_compute_time.percentile))
        logger.info("D2H_latency (ms): min = {0}, max = {1}, mean = {2}, median = {3}, percentile({4}%) = {5}"
                    .format(d2h_latency.min, d2h_latency.max, d2h_latency.mean, d2h_latency.median, scale,
                            d2h_latency.percentile))
        logger.info("throughput 1000*batchsize({})/NPU_compute_time.mean({}): {}".format(
            batchsize, npu_compute_time.mean, throughput))
        logger.info("------------------------------------------------------")

        if output_prefix is not None:
            with open(os.path.join(output_prefix, "sumary.json"), 'w') as f:
                json.dump(self.infodict, f)

summary = Summary()