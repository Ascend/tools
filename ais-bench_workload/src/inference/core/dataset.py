import numpy as np
import os

class DataSet():
    def __init__(self, cache_path, save_result_file_flag=True):
        print("dataset init")
        self.image_list = []
        self.label_list = []
        self.dataset_path = None
        self._preprocessed_data = {}
        self.prediction_items = {}
        self.save_result_file_flag = save_result_file_flag
        if not os.path.exists(cache_path):
            os.mkdir(cache_path)
        self.cache_path = cache_path
        self.predict_result_path = os.path.join(cache_path, "predict_result")
        if not os.path.exists(self.predict_result_path):
            os.mkdir(self.predict_result_path)

    @property
    def get_samples_count(self):
        return len(self.image_list)
        
    def load_query_sample(self, sample_list):
        print("load samples:{}".format(len(sample_list)))
        for index in sample_list:
            processed_img = self.get_processeddata_item(index)
            # print("load index:{} len:{} size:{} shape:{}".format(
            #     index, len(processed_img), processed_img.size, processed_img.shape))
            self._preprocessed_data[index] = processed_img
        return 0

    def unload_query_sample(self, sample_list):
        print("unload samples:{}".format(len(sample_list)))
        if sample_list:
            for index in sample_list:
                del self._preprocessed_data[index]
        return 0

    def preprocess(self, sample_list):
        raise NotImplementedError("Dataset:preprocess")

    def get_preprocessed_data(self, idx_list):
        data = np.array([self._preprocessed_data[idx] for idx in idx_list])
        return (data, )

    def get_predictresult_name(self, sample_id, index):
        return "idx_{}_array_{}.npy".format(sample_id, index)

    def save_predict_result(self, batchsamples, idx_list, outputs_array_list):
        for i, idx in enumerate(idx_list):
            if not batchsamples[i].valid:
                continue
            self.prediction_items[idx] = {}
            for j, outputs_array in enumerate(outputs_array_list):
                if self.save_result_file_flag:
                    file_path = os.path.join(self.predict_result_path, self.get_predictresult_name(idx, j))
                    if file_path.endswith(".npy"):
                        np.save(file_path, outputs_array[i:i+1])
                    else:
                        outputs_array[i:i+1].tofile(file_path)
                else:
                    self.prediction_items[idx][j] = outputs_array

    def get_predict_result(self, sample_id, index):
        if self.save_result_file_flag:
            file_path = os.path.join(self.predict_result_path, self.get_predictresult_name(sample_id, index))
            if file_path.endswith(".npy"):
                array = np.load(file_path)
            else:
                with open(file_path, 'rb') as fd:
                    barray = fd.read()
                    array = np.frombuffer(barray, dtype=np.int8)
            return array
        else:
            return self.prediction_items[sample_id][index]

    # 刷新作业缓存api
    @staticmethod
    def flush_queries():
        self._preprocessed_data.clear()
        self.prediction_items.clear()
        return 0
