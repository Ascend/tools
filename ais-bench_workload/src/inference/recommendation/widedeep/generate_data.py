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

import time
import tensorflow as tf
import tensorflow_transform as tft
import numpy as np
import argparse
import os
import sys


def separate_input_fn(
    tf_transform_output,
    transformed_examples,
    create_batches,
    mode,
    reader_num_threads=1,
    parser_num_threads=2,
    shuffle_buffer_size=10,
    prefetch_buffer_size=1,
    print_display_ids=False):

    filenames_dataset = tf.data.Dataset.list_files(transformed_examples, shuffle=False)
    raw_dataset = tf.data.TFRecordDataset(filenames_dataset, num_parallel_reads=reader_num_threads)

    raw_dataset = raw_dataset.repeat()
    raw_dataset = raw_dataset.batch(create_batches)

    parsed_dataset = raw_dataset.apply(
        tf.data.experimental.parse_example_dataset(
            tf_transform_output.transformed_feature_spec(),
            num_parallel_calls=parser_num_threads
        )
    )

    def consolidate_batch(elem):
        label = elem.pop("label")
        reshaped_label = tf.reshape(label, [-1, label.shape[-1]])
        reshaped_elem = {
            key: tf.reshape(elem[key], [-1, elem[key].shape[-1]])
            for key in elem
        }
        if print_display_ids:
            elem["ad_id"] = tf.Print(input_=elem["ad_id"],
                                     data=[tf.reshape(elem["display_id"],[-1])],
                                     message="display_id", name="print_display_ids",
                                     summarize=elem["ad_id"].shape[1]
                                    )
            elem["ad_id"] = tf.Print(input_=elem["ad_id"],
                                     data=[tf.reshape(elem["ad_id"],[-1])],
                                     message="ad_id", name="print_ad_ids",
                                     summarize=elem["ad_id"].shape[1]
                                    )
            elem["ad_id"] = tf.Print(input_=elem["ad_id"],
                                     data=[tf.reshape(elem["is_leak"],[-1])],
                                     message="is_leak", name="print_is_leak",
                                     summarize=elem["ad_id"].shape[1]
                                    )
        return reshaped_elem, reshaped_label
    parsed_dataset = parsed_dataset.map(
        consolidate_batch,
        num_parallel_calls=None
    )
    return parsed_dataset


def data_generator(tf_records, batchsize):
    tf_transform_output = tft.TFTransformOutput(tf_records)
    eval_file = "{}/eval/part*".format(tf_records)
    local_batch_size = 131072 // 1
    create_batches = local_batch_size // 4096
    parsed_dataset = separate_input_fn(
        tf_transform_output,
        eval_file,
        (32768 // 4096),
        tf.estimator.ModeKeys.EVAL,
        reader_num_threads=1,
        parser_num_threads=1,
        shuffle_buffer_size=int(0.0*create_batches),
        prefetch_buffer_size=1,
        print_display_ids=False)
    iterator = parsed_dataset.make_one_shot_iterator()
    reshaped_elem, reshaped_label = iterator.get_next()

    input_nodes = "ad_advertiser;ad_id;ad_views_log_01scaled;doc_ad_category_id;doc_ad_days_since_published_log_01scaled;doc_ad_entity_id;doc_ad_publisher_id;doc_ad_source_id;doc_ad_topic_id;doc_event_category_id;doc_event_days_since_published_log_01scaled;doc_event_doc_ad_sim_categories_log_01scaled;doc_event_doc_ad_sim_entities_log_01scaled;doc_event_doc_ad_sim_topics_log_01scaled;doc_event_entity_id;doc_event_hour_log_01scaled;doc_event_id;doc_event_publisher_id;doc_event_source_id;doc_event_topic_id;doc_id;doc_views_log_01scaled;event_country;event_country_state;event_geo_location;event_hour;event_platform;event_weekend;pop_ad_id_conf;pop_ad_id_log_01scaled;pop_advertiser_id_conf;pop_advertiser_id_log_01scaled;pop_campain_id_conf_multipl_log_01scaled;pop_campain_id_log_01scaled;pop_category_id_conf;pop_category_id_log_01scaled;pop_document_id_conf;pop_document_id_log_01scaled;pop_entity_id_conf;pop_entity_id_log_01scaled;pop_publisher_id_conf;pop_publisher_id_log_01scaled;pop_source_id_conf;pop_source_id_log_01scaled;pop_topic_id_conf;pop_topic_id_log_01scaled;traffic_source;user_doc_ad_sim_categories_conf;user_doc_ad_sim_categories_log_01scaled;user_doc_ad_sim_entities_log_01scaled;user_doc_ad_sim_topics_conf;user_doc_ad_sim_topics_log_01scaled;user_has_already_viewed_doc;user_views_log_01scaled;display_id"

    for input_node in input_nodes.split(";"):
        sub_dir = "{}".format(input_node)
        if not os.path.exists(sub_dir):
            os.makedirs(sub_dir)
        np_input = reshaped_elem[input_node].eval(session=tf.Session())
        total_num = np_input.shape[0]
        batchs = total_num//batchsize

        for i in range(batchs):
            sub_input = np_input[i*batchsize:(i+1)*batchsize]
            sub_input.tofile(os.path.join(sub_dir, "{}.bin".format(str(i).zfill(6))))
    labels = reshaped_label.eval(session=tf.Session())
    if not os.path.exists('labels'):
        os.makedirs("labels")

    total_num = labels.shape[0]
    batchs = total_num // batchsize
    for i in range(batchs):
        sub_input = labels[i*batchsize:(i+1)*batchsize]
        sub_input.tofile(os.path.join('labels', "{}.bin".format(str(i).zfill(6))))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_path", type=str, default='./outbrain/tfrecords')
    parser.add_argument("--batchsize", type=int, default=1024)
    args = parser.parse_args()
    data_generator(args.data_path, args.batchsize)
