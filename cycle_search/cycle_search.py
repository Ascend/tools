import argparse
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

def get_node_name(tensor_name):
    if tensor_name.startswith("^"):
        return tensor_name[1:]
    return tensor_name.split(":")[0]

def build_node_connect_summary(graph_def):
    node_connect_map = {}
    for node in graph_def.node:
        node_name = get_node_name(node.name)
        in_node_names = set()
        for in_name in node.input:
            in_node_name = get_node_name(in_name)
            in_node_names.add(in_node_name)
        node_connect_map[node_name] = in_node_names
    return node_connect_map

def find_net_output_node_name(graph_def):
    for node in graph_def.node:
        if node.op_type == "ge:NetOutput":
            return get_node_name(node.name)
    print("[ERROR] not found default NetOutput node, please give end node param")

def print_cycle_nodes(road_list, cycle_node_name):
    travel_node = road_list.pop()
    while travel_node != cycle_node_name:
        print("road node_name : " + travel_node)
        travel_node = road_list.pop()

class main(object):
    @staticmethod
    def get_travel_node(input_path, src_node=None):
        print("[INFO] load graph from ", input_path)
        graph_def = load_graph_def_from_pb(input_path)

        print("[INFO] build_node_connect_summary start")
        node_connect_map = build_node_connect_summary(graph_def)

        if src_node == None:
            src_node = find_net_output_node_name(graph_def)
            print("[INFO] choose default NetOutput end node : " + src_node + " to be start")

        print("[INFO] graph travel start, from end node : ", src_node)

        road_list = []
        road_set = set()
        history = set()

        def TravelInputs(node_connect_map, curr_node_name, road_list, road_set, history):
            if curr_node_name in road_set:
                print("[FINAL] found cycle for node : ", curr_node_name)
                print_cycle_nodes(road_list, curr_node_name)
                sys.exit()
            #print("[DEBUG] push node ", curr_node_name)
            road_list.append(curr_node_name)
            road_set.add(curr_node_name)
            if curr_node_name in history:
                #print("[DEBUG] history has traveled node : ", curr_node_name)
                return
            for in_node_name in node_connect_map[curr_node_name]:
                if in_node_name == "":
                    continue
                TravelInputs(node_connect_map, in_node_name, road_list, road_set, history)
                #print("[DEBUG] pop node ", in_node_name)
                road_list.pop()
                road_set.remove(in_node_name)
            history.add(curr_node_name)

        TravelInputs(node_connect_map, src_node, road_list, road_set, history)
        print("[FINAL] not found cycle nodes")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    #travel
    subparser = subparsers.add_parser("travel", help="travel graph to search cycle nodes")
    subparser.add_argument("--input", dest="input_path", required=True, help="input onnx dump graph path")
    subparser.add_argument("--node", dest="src_node", default=None, help="input source node to start travel")
    subparser.set_defaults(func=main.get_travel_node)

    if len(sys.argv) <= 2:
        parser.print_help()
        sys.exit()

    (args, unknown) = parser.parse_known_args()

    func = args.func
    del args.func

    args = dict(filter(lambda x: x[1], vars(args).items()))
    func(**args)
