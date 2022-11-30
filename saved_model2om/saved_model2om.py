import os
import argparse
import sys
import subprocess

import tensorflow as tf
from tensorflow.python.tools import saved_model_cli
from tensorflow.python.saved_model import tag_constants
from tensorflow.python.saved_model import signature_constants
from six import StringIO
import contextlib
import time
import shutil


@contextlib.contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr

    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr
    finally:
        sys.stdout, sys.stderr = old_out, old_err


def get_input_output_node(saved_model_dir, saved_tags, sign):

    parser = saved_model_cli.create_parser()
    saved_model_cli_args = parser.parse_args([
        'show',
        '--dir', saved_model_dir,
        '--tag_set', saved_tags,
        '--signature_def', sign
    ])

    with captured_output() as (out, err):
        saved_model_cli.show(saved_model_cli_args)

    result = out.getvalue().strip()
    print(result)

    input_nodes = {}
    output_nodes = []
    lines = result.split('\n')
    for idx, line in enumerate(result.split('\n')):
        if "inputs[" in line:
            shape_line = lines[idx + 2]
            name_line = lines[idx + 3]
            input_name = name_line.split(":")[1].strip()
            input_shape = tuple(int(shape) for shape in shape_line.split(":")[1].strip()[1:-1].split(","))
            input_nodes[input_name] = input_shape
        if "outputs[" in line:
            line = lines[idx + 3]
            output = line.split(":")[1].strip()
            output_nodes.append(output)

    if not output_nodes:
        raise RuntimeError("No Output Nodes found in saved_model.")

    return input_nodes, output_nodes


def saved_pb(saved_model_dir, output_nodes, output_dir, output_name, saved_tags):
    with tf.Session(graph=tf.Graph()) as sess:
        tf.saved_model.load(sess, saved_tags, saved_model_dir)
        graph = tf.compat.v1.graph_util.convert_variables_to_constants(sess, input_graph_def=sess.graph.as_graph_def(),
                                                                       output_node_names=output_nodes)

        tf.io.write_graph(
            graph,
            output_dir,
            output_name,
            as_text=False
        )

        return tuple(tensor.name for tensor in graph.node)


def saved_model_to_pb(saved_model_dir, output_dir, output_name, saved_tags=tag_constants.SERVING,
                      sign=signature_constants.DEFAULT_SERVING_SIGNATURE_DEF_KEY):

    input_nodes, output_nodes = get_input_output_node(saved_model_dir, saved_tags, sign)

    print("[INFO]: Save Model has [", len(output_nodes), "] outputs.")
    print("[INFO]: Outputs Nodes: ", output_nodes, ".")

    saved_node_names = saved_pb(saved_model_dir, output_nodes, output_dir, output_name, [saved_tags])

    remove_keys = []
    for key in input_nodes:
        if key not in saved_node_names:
            remove_keys.append(key)

    for key in remove_keys:
        input_nodes.pop(key)
    print("[INFO]: Inputs Nodes With Shapes: ", input_nodes, ".")
    print("[INFO]: Saved Model convert to Frozen Model done.")
    return input_nodes


def gen_pb_txt(pb_file_path):
    func2graph_path_in_home = os.path.join("Ascend", "ascend-toolkit", "latest", "atc", "python", "func2graph",
                                           "func2graph.py")
    func2graph_path = os.path.join(os.getenv("HOME"), func2graph_path_in_home)
    if not os.path.exists(func2graph_path):
        func2graph_path = os.path.join("/usr/local", func2graph_path_in_home)
    subprocess.run(("python3", func2graph_path, "-m", pb_file_path), stdout=subprocess.PIPE)


def pb_to_om(pb_file_path, output_path, soc_version, input_shape, rest_args):
    atc_path_in_home = os.path.join("Ascend", "ascend-toolkit", "latest", "bin", "atc")
    atc_path = os.path.join(os.getenv("HOME"), atc_path_in_home)
    if not os.path.exists(atc_path):
        atc_path = os.path.join("/usr/local", atc_path_in_home)
    subprocess.run((atc_path, "--framework", "3", "--model", pb_file_path, "--output", output_path, "--soc_version",
                    soc_version, "--input_shape", input_shape, *rest_args))


def pb_to_om_with_profiling(pb_file_path, output_path, input_shape, profiling, rest_args):
    aoe_path_in_home = os.path.join("Ascend", "ascend-toolkit", "latest", "bin", "aoe")
    aoe_path = os.path.join(os.getenv("HOME"), aoe_path_in_home)
    if not os.path.exists(aoe_path):
        aoe_path = os.path.join("/usr/local", aoe_path_in_home)
    subprocess.run((aoe_path, "--framework", "3", "--model", pb_file_path, "--output",
                    output_path, "--input_shape", input_shape, "--job_type", profiling, *rest_args))


def get_input_shape(input_nodes):
    input_shapes = []
    for key, value in input_nodes.items():
        input_shapes.append(f"{key}:{','.join('1' if shape == -1 else str(shape) for shape in value)}")
    input_shape_param = ";".join(input_shapes)
    print(f"Because the input_shape parameter is not set, the following values are used: {input_shape_param}")
    return input_shape_param


def main(input_path, output_path, input_shape, soc_version, profiling, rest_args):
    tmp_path = os.path.join("/tmp", f"pb_dir_{int(time.time())}")
    os.makedirs(tmp_path, exist_ok=True)
    tmp_pb_name = "model.pb"
    tmp_pb_file = os.path.join(tmp_path, tmp_pb_name)
    input_nodes = saved_model_to_pb(input_path, tmp_path, tmp_pb_name)
    if not input_shape:
        input_shape = get_input_shape(input_nodes)
    gen_pb_txt(tmp_pb_file)

    if profiling is not None:
        pb_to_om_with_profiling(tmp_pb_file, output_path, input_shape, profiling, rest_args)
    else:
        pb_to_om(tmp_pb_file, output_path, soc_version, input_shape, rest_args)
    shutil.rmtree(tmp_path)


def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_path", required=True, help='SavedModel path.')
    parser.add_argument("--output_path", required=True,
                        help="Output file path&name(needn't suffix, will add .om automatically).")
    parser.add_argument("--input_shape", default='', help='Shape of input data. '
                                                          'Separate multiple nodes with semicolons (;). '
                                                          'Use double quotation marks (") to enclose each argument.'
                                                          'E.g.: "input_name1:n1,c1,h1,w1;input_name2:n2,c2,h2,w2"')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--soc_version", help="The soc version. "
                                             "This parameter is not required when profiling is set.")
    group.add_argument("--profiling", choices=['1', '2'], help="Set this parameter when profiling is required."
                                                               "(sgat: 1, opat: 2).")
    return parser.parse_known_args()


if __name__ == "__main__":
    args, unknown_args = get_args()
    main(args.input_path, args.output_path, args.input_shape, args.soc_version, args.profiling, unknown_args)
