# Copyright 2017 The TensorFlow Authors. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ============================================================================
# Copyright 2021 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# Copyright 2017 Max Planck Society
# Distributed under the BSD-3 Software license,
# (See accompanying file ./LICENSE.txt or copy at
# https://opensource.org/licenses/BSD-3-Clause)
import os
import argparse

import numpy as np
import tensorflow as tf


def write_accuracy(result_file, result_content):

    import json
    encode_json = json.dumps(result_content, sort_keys=False, indent=4)
    with open(result_file, "w") as json_file:
        json_file.write(encode_json)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # -----------------------------------------------------
    parser.add_argument("--infer_result", type=str, default="../../result_Files")
    parser.add_argument("--num_output", type=int, default=1)
    parser.add_argument("--data_type", type=str, default="float32")
    parser.add_argument("--result_file", type=str, default="./accuracy_result.json")
    parser.add_argument("--display_id", type=str, default="../display_id")
    parser.add_argument("--label", type=str, default="../data/labels")
    parser.add_argument("--offset", type=int, default=1)
    # ----------------------------------------------------
    args = parser.parse_args()
    predictions = []
    display_id = []
    labels = []
    file_list = os.listdir(args.infer_result)
    file_list.sort()
    for file in file_list:
        if file.endswith(".bin"):
            now_data = np.fromfile(os.path.join(args.infer_result, file), dtype=np.float32)
            predictions.append(now_data)
            id = np.fromfile(os.path.join(args.display_id, "{}.bin".format(file.split("davinci_")[1].split("_output")[0])), dtype=np.int64)
            display_id.append(id)
            label = np.fromfile(os.path.join(args.label, "{}.bin".format(file.split("davinci_")[1].split("_output")[0])), dtype=np.int64)
            labels.append(label)
    predictions = np.array(predictions).reshape(-1, 1)
    display_id = np.array(display_id).reshape(-1)
    labels = np.array(labels).reshape(-1)
    print("predictions:", predictions.shape)
    print("display_id:", display_id.shape)
    print("labels:", labels.shape)
    display_ids = tf.reshape(display_id, [-1])
    predictions = predictions[:, 0]
    sorted_ids = tf.argsort(display_ids)
    display_ids = tf.gather(display_ids, indices=sorted_ids)
    predictions = tf.gather(predictions, indices=sorted_ids)
    labels = tf.gather(labels, indices=sorted_ids)

    _, display_ids_idx, display_ids_ads_count = tf.unique_with_counts(
        display_ids, out_idx=tf.int64)
    pad_length = 30 - tf.reduce_max(display_ids_ads_count)
    pad_fn = lambda x: tf.pad(x, [(0, 0), (0, pad_length)])

    preds = tf.RaggedTensor.from_value_rowids(predictions, display_ids_idx).to_tensor()
    labels = tf.RaggedTensor.from_value_rowids(labels, display_ids_idx).to_tensor()
    labels = tf.argmax(labels, axis=1)
    map_tensor = tf.metrics.average_precision_at_k(
        predictions=pad_fn(preds),
        labels=labels,
        k=12,
        name="streaming_map_with_leak")
    accuracy_results = {}
    with tf.Session() as sess:
        sess.run(tf.global_variables_initializer())
        sess.run(tf.local_variables_initializer())
        accuracy_results["Acc"] = sess.run(map_tensor)[1]
    print("Acc:", accuracy_results['Acc'])
    write_accuracy(args.result_file, accuracy_results)
