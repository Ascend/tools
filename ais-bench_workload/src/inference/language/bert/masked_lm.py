import os
import pickle
import numpy as np
import dataset
import tokenization
import tensorflow as tf
import random

from logger import log
from create_maskedlm_data import create_training_instances, write_instance_to_example_files

class MaskedLM(dataset.DataSet):
    def __init__(self, data_path, vocab_path, cache_path, count):
        super(MaskedLM, self).__init__(cache_path)
        self.vocab_path = vocab_path
        self.data_path = data_path
        self.count = count

    @property
    def get_samples_count(self):
        if self.count > 0:
            return self.count
        return 60
        #return len(self.eval_features)

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
        self.eval_features = self.pre_proc() # length=10833
        return 0

    def pre_proc(self):
        self.max_seq_length = 128
        self.do_lower_case = True
        self.max_predictions_per_seq = 20
        self.random_seed = 12345
        self.dupe_factor = 5
        self.masked_lm_prob = 0.12345
        self.short_seq_prob = 0.1
        eval_features = []
        # Load features if cached, convert from examples otherwise.
        cache_file_path = os.path.join(self.cache_path, 'eval_features.pickle')
        if os.path.exists(cache_file_path):
            log.info("Loading cached features from '%s'..." % cache_file_path)
            with open(cache_file_path, 'rb') as cache_file:
                eval_features = pickle.load(cache_file)
        else:
            log.info("Creating tokenizer...")
            tokenizer = tokenization.FullTokenizer(vocab_file=self.vocab_path, do_lower_case=self.do_lower_case)

            log.info("Converting examples to features...")
            def append_feature(feature):
                eval_features.append(feature)
            
            input_files = []
            for input_pattern in self.data_path.split(","):
                input_files.extend(tf.gfile.Glob(input_pattern))
            rng = random.Random(self.random_seed)
            instances = create_training_instances(
                input_files, tokenizer, self.max_seq_length, self.dupe_factor,
                self.short_seq_prob, self.masked_lm_prob, self.max_predictions_per_seq,
                rng)

            write_instance_to_example_files(instances,
                                            tokenizer,
                                            self.max_seq_length,
                                            self.max_predictions_per_seq,
                                            output_fn=append_feature)

            log.info("Caching features at '%s'..." % cache_file_path)
            with open(cache_file_path, 'wb') as cache_file:
                pickle.dump(eval_features, cache_file)
        print("len(eval_features)", len(eval_features))
        return eval_features

    def get_preprocessed_data(self, id_list):
        input_ids = np.array([self.eval_features[id].input_ids for id in id_list], dtype=np.int32)
        input_mask = np.array([self.eval_features[id].input_mask for id in id_list], dtype=np.int32)
        segment_ids = np.array([self.eval_features[id].segment_ids for id in id_list], dtype=np.int32)
        masked_lm_positions = np.array([self.eval_features[id].masked_lm_positions for id in id_list], dtype=np.int32)
        return input_ids, input_mask, segment_ids, masked_lm_positions

    def flush_queries(self):
        del self.eval_features
        return 0

class PostProcessBase:
    def __init__(self):
        self.accuracy = 0.0

    # 后处理函数 对推理的结果进行处理和获取准确度等值，
    # 注意该函数必须要返回准确率信息
    def post_proc_func(self, sample_list):
        self.post_proc()
        return self.accuracy

class PostProcessMaskedLM(PostProcessBase):
    def __init__(self, dataset_path=None):
        super(PostProcessMaskedLM, self).__init__()

    def post_proc(self):
        pass