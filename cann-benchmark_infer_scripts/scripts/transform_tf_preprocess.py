"""
    Copyright 2020 Huawei Technologies Co., Ltd

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
    Typical usage example:
"""

import operator
import os
import sys
import numpy as np

from tensor2tensor.data_generators import text_encoder
import tensorflow.compat.v1 as tf

res = []


def decode_from_file(vocabularypath, savepath, filename):
    """Compute predictions on entries in filename and write them out."""
    batch_size = 1
    # Inputs vocabulary is set to targets if there are no inputs in the problem,
    # e.g., for language models where the inputs are just a prefix of targets.
    inputs_vocab = text_encoder.SubwordTextEncoder(vocabularypath)
    tf.logging.info("Performing decoding from file (%s)." % filename)
    sorted_inputs, sorted_keys = _get_sorted_inputs(
        filename)
    # the number of sentences
    num_sentences = len(sorted_inputs)
    # the number of batch need to process
    num_decode_batches = (num_sentences - 1) // batch_size + 1
    print(num_decode_batches)
    _decode_batch_input_fn(num_decode_batches,
                           sorted_inputs, inputs_vocab,
                           batch_size=1, max_input_size=-1,
                           has_input=True, savepath=savepath,
                           sorted_keys=sorted_keys)


def _get_sorted_inputs(filename, delimiter="\n"):
    """Returning inputs sorted by decreasing length.

      This causes inputs of similar lengths to be processed in the same batch,
      facilitating early stopping for short sequences.

      Longer sequences are sorted at the first time so that if you're going to get OOMs,
      you'll get it in the first batch.

      Args:
        filename: path to file with inputs, 1 per line.
        delimiter: str, delimits records in the file.

      Returns:
        a sorted list of inputs

      """
    tf.logging.info("Getting sorted inputs")
    with tf.gfile.Open(filename) as file:
        text = file.read()
        split_items = text.split(delimiter)
        input_items = [record.strip() for record in split_items]
        # Strip the last empty line.
        if not input_items[-1]:
            input_items.pop()
    input_lengths = [(i, -len(line.split())) for i, line in enumerate(input_items)]
    sorted_input_lengths = sorted(input_lengths, key=operator.itemgetter(1))
    # We'll need the keys to rearrange the inputs back into their original order
    sorted_keys = {}
    sorted_input_items = []
    for i, (index, _) in enumerate(sorted_input_lengths):
        sorted_input_items.append(input_items[index])
        sorted_keys[i] = index
    return sorted_input_items, sorted_keys


def _decode_batch_input_fn(num_decode_batches, sorted_inputs, vocabulary,
                           batch_size, max_input_size,
                           task_id=-1, has_input=True, savepath='./input_bin',
                           sorted_keys=None):
    """Generator to produce batches of inputs."""
    tf.logging.info(" batch %d" % num_decode_batches)
    savepath = savepath
    for batch in range(num_decode_batches):
        tf.logging.info("Decoding batch %d" % batch)
        batch_length = 0
        batch_inputs = []
        for inputs in sorted_inputs[batch * batch_size:(batch + 1) * batch_size]:
            input_ids = vocabulary.encode(inputs)
            if max_input_size > 0:
                # Subtract 1 for the EOS_ID.
                input_ids = input_ids[:max_input_size - 1]
            if has_input or task_id > -1:  # Do not append EOS for pure LM tasks.
                final_id = text_encoder.EOS_ID if task_id < 0 else task_id
                input_ids.append(final_id)
            batch_inputs.append(input_ids)
            if len(input_ids) > batch_length:
                batch_length = len(input_ids)
        final_batch_inputs = []
        for input_ids in batch_inputs:
            assert len(input_ids) <= batch_length
            x = input_ids + [0] * (batch_length - len(input_ids))
            final_batch_inputs.append(x)
        tmp = np.array(list(final_batch_inputs[0])).astype(np.int32)

        if len(tmp) < 128:
            data_input = np.zeros((1, 128), np.int32)
            data_input[:, :len(tmp)] = tmp

        data_input.tofile(os.path.join(savepath, str(batch) +
                                       '_' + str(sorted_keys[batch]) + ".bin"))
        print(os.path.join(savepath, str(batch) + '_' +
                           str(sorted_keys[batch]) + ".bin") + 'already created')

        res.append(final_batch_inputs)


if __name__ == '__main__':
    """
    vocabularypath dict path './vocab.translate_ende_wmt32k.32768.subwords'
    filename waited translate file path './test_data/newstest2014.en'
    savepath output bin file path './input_bin_sort'
    python3 ./preprocess_transform.py ./vocab.translate_ende_wmt32k.32768.subwords
           ./newstest2014.en ./input_bin_sort
    """
    if len(sys.argv) < 4:
        raise Exception("usage: python3 xxx.py [vocabularypath] "
                        "[src_path] [save_path]")
    vocabularypath = sys.argv[1]
    filename = sys.argv[2]
    savepath = sys.argv[3]

    vocabularypath = os.path.realpath(vocabularypath)
    filename = os.path.realpath(filename)
    savepath = os.path.realpath(savepath)
    if not os.path.isdir(savepath):
        os.makedirs(savepath)
    decode_from_file(vocabularypath, savepath, filename)
