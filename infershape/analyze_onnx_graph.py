import onnx
import os
import sys

from google.protobuf import text_format


def load_graph_def_from_pb(path):
    with open(path, "rb") as f:
        data = f.read()
        model = onnx.ModelProto()
        text_format.Parse(data, model)
    return model.graph

def get_node_dtype(n, i):
    dtype_attr = None
    for attr in n.attribute:
        if (attr.name == "output_desc_dtype:" + str(i)):
            dtype_attr = attr
    if (dtype_attr == None):
        return "DT_INVALID"
    return dtype_attr.s.decode()

def get_node_shape(n, i):
    shape_attr = None
    for attr in n.attribute:
        if (attr.name == "output_desc_shape:" + str(i)):
            shape_attr = attr
    if (shape_attr == None):
        return []
    return "[" + ",".join('%s' %id for id in shape_attr.ints) + "]"

if __name__ == "__main__":
    if (len(sys.argv) != 2):
        print("[ERROR]please input onnx graph name")
        exit(0)
    graph_def = load_graph_def_from_pb(sys.argv[1])

    total_content = ""
    for node in graph_def.node:
        index = 0
        for out in node.output:
            if (out[-2] == '-'):
                continue
            shape = get_node_shape(node, index)
            dtype = get_node_dtype(node, index)
            item = "node:" + node.name + " index:" + str(index) + " shape:" + shape + " dtype:" + dtype + "\n"
            total_content += item
            index = index + 1

    with open("npu_infershape_result", "w") as result_file:
        result_file.write(total_content)
