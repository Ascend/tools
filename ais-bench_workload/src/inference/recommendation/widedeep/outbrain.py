import json
import os
import sys

import ais_utils
import dataset
from loadgen_interface import LoadgenInterface


class Outbrain(dataset.DataSet):
    def __init__(self, cache_path=os.getcwd()):
        super(Outbrain, self).__init__(cache_path)
        self.cur_path = os.path.dirname(os.path.realpath(__file__))
        self.output_dir = os.path.join(self.cur_path, 'results')
        self.args = None
        self.infer_log = os.path.join(self.cur_path, "benchmark.log")

    @property
    def get_samples_count(self):
        """
        获取样本个数。loadgen将根据样本个数进行调度和计算
        """
        return 100

    def pre_proc_func(self, sample_list):
        """
        loadgen预处理接口 传入数据索引list 进行数据处理
        :param sample_list: 数据索引list
        :return: True: 操作成功; False: 操作失败
        """
        cmd = "{} -u {}/generate_data.py --data_path {} --batchsize {}".format(
            sys.executable, self.cur_path, self.args.dataset_path, self.args.batchsize)
        ret = os.system(cmd)
        if ret != 0:
            raise RuntimeError("cmd:{} run failed".format(cmd))
        print("pre process run:{} done".format(cmd))
        return 0

    def predict_proc_func(self, query_samples):
        """
        loadgen推理接口 传入数据索引query_samples 进行推理
        :param query_samples: 数据索引list
        :return: True: 操作成功; False: 操作失败
        """
        print("predict query samples size:{}".format(len(query_samples)))

        os.system("rm -rf {};mkdir -p {}".format(self.output_dir, self.output_dir))

        input = "\"ad_advertiser,ad_id,ad_views_log_01scaled,doc_ad_category_id,doc_ad_days_since_published_log_01scaled,doc_ad_entity_id,doc_ad_publisher_id,doc_ad_source_id,doc_ad_topic_id,doc_event_category_id,doc_event_days_since_published_log_01scaled,doc_event_doc_ad_sim_categories_log_01scaled,doc_event_doc_ad_sim_entities_log_01scaled,doc_event_doc_ad_sim_topics_log_01scaled,doc_event_entity_id,doc_event_hour_log_01scaled,doc_event_id,doc_event_publisher_id,doc_event_source_id,doc_event_topic_id,doc_id,doc_views_log_01scaled,event_country,event_country_state,event_geo_location,event_hour,event_platform,event_weekend,pop_ad_id_conf,pop_ad_id_log_01scaled,pop_advertiser_id_conf,pop_advertiser_id_log_01scaled,pop_campain_id_conf_multipl_log_01scaled,pop_campain_id_log_01scaled,pop_category_id_conf,pop_category_id_log_01scaled,pop_document_id_conf,pop_document_id_log_01scaled,pop_entity_id_conf,pop_entity_id_log_01scaled,pop_publisher_id_conf,pop_publisher_id_log_01scaled,pop_source_id_conf,pop_source_id_log_01scaled,pop_topic_id_conf,pop_topic_id_log_01scaled,traffic_source,user_doc_ad_sim_categories_conf,user_doc_ad_sim_categories_log_01scaled,user_doc_ad_sim_entities_log_01scaled,user_doc_ad_sim_topics_conf,user_doc_ad_sim_topics_log_01scaled,user_has_already_viewed_doc,user_views_log_01scaled\""
        cmd = "{}/benchmark --model {} --input {} --output {} > {}".format(
            self.cur_path, self.args.model, input, self.output_dir, self.infer_log)
        ret = os.system(cmd)
        if ret != 0:
            raise RuntimeError("cmd:{} run failed".format(cmd))
        print("predict run:{} done".format(cmd))

        LoadgenInterface.send_response(self, query_samples)
        print("predict send response done")
        return 0

    def get_processeddata_item(self, nr):
        return None

    def post_proc_func(self, sample_list):
        """
        loadgen后处理接口 传入数据索引list 进行数据处理
        :param sample_list: 数据索引list
        :return: True: 操作成功; False: 操作失败
        """
        cmd = "{} -u {}/postprocess.py --infer_result {} --display_id={}/display_id/ --label={}/labels/".format(
            sys.executable, self.cur_path, self.output_dir, self.cur_path, self.cur_path)
        ret = os.system(cmd)
        if ret != 0:
            raise RuntimeError("cmd:{} run failed".format(cmd))
        print("post process run:{} done".format(cmd))
        # 获取准确率
        accuracy = 0.0
        with open('accuracy_result.json', 'r') as load_f:
            load_dict = json.load(load_f)
            accuracy = load_dict['Acc']

        infer_latency = 0
        with open("./benchmark.log", 'r') as f:
            lines = f.readlines()
            for line in lines:
                if "Inference average time without first time" in line:
                    acc_str = line.split(':')[1]
                    infer_latency = float(acc_str[:-3])
                    break
        ais_utils.set_result("inference", "infer_latency", infer_latency)
        return accuracy
