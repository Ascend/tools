import os
import json
import pickle
import subprocess
import collections

import numpy as np
import dataset

from logger import log
from transformers import BertTokenizer
from create_squad_data import read_squad_examples
from create_squad_data import convert_examples_to_features
from postprocess import write_predictions

class Squad(dataset.DataSet):
    def __init__(self, data_path, vocab_path, cache_path, count):
        super(Squad, self).__init__(cache_path)
        self.data_path = data_path
        self.vocab_path = vocab_path
        log.info("Reading examples...")
        self.eval_examples = read_squad_examples(input_file=self.data_path,
            is_training=False, version_2_with_negative=False) # length=10570
        self.count = count

    @property
    def get_samples_count(self):
        if self.count > 0:
            return self.count
        return 10833
        # return len(self.eval_features)

    # 根据参数加载样本到内存中 api
    # 当前样例已经在preprocess中加载到了内存中 该函数内不需加载
    def load_query_sample(self, sample_list):
        return 0
        # log.info("load samples:{}".format(sample_list))

    # 释放样本api
    def unload_query_sample(self, sample_list):
        return 0
        # log.info("unload samples:{}".format(sample_list))


    def pre_proc_func(self, sample_list):
        self.eval_features = self.pre_proc(self.eval_examples) # length=10833
        return 0

    def pre_proc(self, examples):
        self.max_seq_length = 384
        self.max_query_length = 64
        self.doc_stride = 128
        eval_features = []
        cache_path='eval_features.pickle'
        # Load features if cached, convert from examples otherwise.
        if os.path.exists(cache_path):
            log.info("Loading cached features from '%s'..." % cache_path)
            with open(cache_path, 'rb') as cache_file:
                eval_features = pickle.load(cache_file)
        else:
            log.info("Creating tokenizer...")
            tokenizer = BertTokenizer(self.vocab_path)

            log.info("Converting examples to features...")
            def append_feature(feature):
                eval_features.append(feature)

            convert_examples_to_features(
                examples=examples,
                tokenizer=tokenizer,
                max_seq_length=self.max_seq_length,
                doc_stride=self.doc_stride,
                max_query_length=self.max_query_length,
                is_training=False,
                output_fn=append_feature,
                verbose_logging=False)

            log.info("Caching features at '%s'..." % cache_path)
            with open(cache_path, 'wb') as cache_file:
                pickle.dump(eval_features, cache_file)
        print("len(eval_features)", len(eval_features))
        return eval_features

    def get_preprocessed_data(self, id_list):
        input_ids = np.array([self.eval_features[id].input_ids for id in id_list], dtype=np.int32)
        input_mask = np.array([self.eval_features[id].input_mask for id in id_list], dtype=np.int32)
        segment_ids = np.array([self.eval_features[id].segment_ids for id in id_list], dtype=np.int32)
        return input_ids, input_mask, segment_ids

    def flush_queries(self):
        del self.eval_features
        del self.eval_examples
        return 0


RawResult = collections.namedtuple("RawResult", ["unique_id", "start_logits", "end_logits"])

class PostProcessBase:
    def __init__(self):
        self.exact_match = 0.0
        self.f1 = 0.0

    # 后处理函数 对推理的结果进行处理和获取准确度等值，
    # 注意该函数必须要返回准确率信息
    def post_proc_func(self, sample_list):
        self.post_proc(sample_list)
        return self.f1

class PostProcessSquad(PostProcessBase):
    def __init__(self, dataset_path=None):
        super(PostProcessSquad, self).__init__()

    def post_proc(self, sample_list):
        n = len(sample_list)
        results = []
        for i in range(n):
            output_array = self.datasets.get_predict_result(i, 0)
            m = len(output_array)
            for j in range(m):
                start_logits = output_array[:,:,0]
                end_logits = output_array[:,:,1]
                result = RawResult(unique_id=int(self.datasets.eval_features[i].unique_id),
                    start_logits=start_logits[j].tolist(),
                    end_logits=end_logits[j].tolist())
                results.append(result)

        log.info("Post-processing predictions...")

        output_pre = "./postproc"
        output_prediction_file = output_pre + "_predictions.json"
        output_nbest_file = output_pre + "_nbest_predictions.json"

        write_predictions(self.datasets.eval_examples, self.datasets.eval_features, results, 20, 30, True, output_prediction_file, output_nbest_file)

        log.info("Evaluating predictions...")

        cmd = "python3 ./evaluate-v1.1.py {} {}".format(self.datasets.data_path, output_prediction_file)
        subprocess.check_call(cmd, shell=True)
        with open('evaluate.json','r') as load_f:
            load_dict = json.load(load_f)
            self.exact_match = load_dict['exact_match']
            self.f1 = load_dict['f1']

    def set_datasets(self, datasets):
        self.datasets = datasets