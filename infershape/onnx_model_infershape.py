import os
import onnx
import numpy as np
import onnxruntime as rt
from onnx import helper,shape_inference,TensorProto


import argparse

parser = argparse.ArgumentParser(usage='use -h/--help to show tips', description='help info')
parser.add_argument('-m', '--model', required=True, dest='model_path', help='onnx model file')
parser.add_argument('-i', '--input_shape', default='', dest='input_shape', help='model input shapes')
parser.add_argument('-o', '--output', default='cpu_infershape_result', dest='output_file', help='result file path')
args = parser.parse_args()


ONNX_DTYPE = {
    0: TensorProto.FLOAT,
    1: TensorProto.FLOAT,
    2: TensorProto.UINT8,
    3: TensorProto.INT8,
    4: TensorProto.UINT16,
    5: TensorProto.INT16,
    6: TensorProto.INT32,
    7: TensorProto.INT64,
    8: TensorProto.STRING,
    9: TensorProto.BOOL
}


def get_tensor_shape(tensor):
    dims = tensor.type.tensor_type.shape.dim
    n = len(dims)
    return [dims[i].dim_value for i in range(n)]


def rewrite_input_shape(graph,shape_dict):
    for input_tensor in graph.input:
        if shape_dict.__contains__(input_tensor.name):
            input_tensor_new = onnx.helper.make_tensor_value_info(name=input_tensor.name, elem_type=1,
                                                                  shape=shape_dict[input_tensor.name])
            graph.input.remove(input_tensor)
            graph.input.insert(0, input_tensor_new)


def pre_process(onnx_model):
    if args.input_shape == '':
        return onnx_model
    shape_dict={}
    for tensor_shape in args.input_shape.split(';'):
        node_name = tensor_shape[:tensor_shape.rfind(':')]
        shapes = tensor_shape[tensor_shape.rfind(':')+1:]
        shape_dict[node_name] = [int(dim) for dim in shapes.split(',')]
    rewrite_input_shape(onnx_model.graph, shape_dict)

def runtime_infer(onnx_model):
    pre_process(onnx_model)
    graph = onnx_model.graph
    for i, tensor in enumerate(graph.value_info):
        graph.output.insert(i + 1, tensor)
    model_file = "onnx_infer_temp.onnx"
    onnx.save(onnx_model, model_file)

    sess = rt.InferenceSession(model_file)

    in_name = [ip.name for ip in sess.get_inputs()]
    input_map = {}
    for ip in graph.input:
        if in_name.__contains__(ip.name):
            input_shape = get_tensor_shape(ip)
            input_map[ip.name] = np.ones(input_shape, dtype=np.float32)
        pass
    out_name = [out_node.name for out_node in sess.get_outputs()]

    outputs = {}
    tensors = sess.run(out_name, input_map)
    for i, name in enumerate(out_name):
        outputs[name] = np.array(tensors[i]).shape

    os.remove(model_file)
    return outputs


def post_process(graph, output_dict):
    # parse input and const node shape:
    const_names = []
    for init in graph.initializer:
        const_names.append(init.name)
    # ge::onnx_parser will sort const nodes with std::map before rename
    const_names.sort()

    input_dict = {}
    for input_node in graph.input:
        shape_values = ','.join(str(dim.dim_value) for dim in input_node.type.tensor_type.shape.dim)
        const_node_name = '_'.join([input_node.name, str(const_names.index(input_node.name))]) if const_names.count(
            input_node.name) != 0 else input_node.name
        input_dict[input_node.name] = [const_node_name, shape_values]


    # extract output shape for node
    cpu_infer_result = ''
    for i, node in enumerate(graph.node):
        node_name = node.name if node.name != '' else '{}_{}'.format(node.op_type, i)
        # const or data
        for input_name in node.input:
            if input_dict.__contains__(input_name):
                cpu_infer_result += 'node:{} index:0 shape:[{}]\n'.format(input_dict[input_name][0],
                                                                          input_dict[input_name][1])
        for idx, output_name in enumerate(node.output):
            # print("output name:",output_name)
            if output_dict.__contains__(output_name):
                cpu_infer_result += 'node:{} index:{} shape:[{}]\n'.format(node_name, idx, ','.join([str(i) for i in output_dict[output_name]]))
            else:
                print('The {} output shape for node {} was not found.'.format(idx, node_name))

    with open(args.output_file, 'w') as f:
        f.write(cpu_infer_result)
    pass


def infer_shape(model_file):
    onnx_model = onnx.load(model_file)
    onnx.checker.check_model(model_file)

    processed_model = shape_inference.infer_shapes(onnx_model)
    infer_result = runtime_infer(processed_model)
    return processed_model, infer_result


if __name__ == "__main__":
    model = args.model_path
    infered_model, output = infer_shape(model)
    post_process(infered_model.graph, output)
