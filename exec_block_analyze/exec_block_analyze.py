#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
import argparse
import collections

SAVE_PICTURE = True

DUMP_TEXT_NODES = True
DUMP_TEXT_STREAM_NODES = True
DUMP_TEXT_NODE_ACTIVED_STREAMS = True
DUMP_TEXT_STREAM_ACTIVED_STREAMS = True
DUMP_TEXT_MEMORY = False

SAVE_SEQUENCE = True

SAVE_STREAMS = True
SAVE_STREAMS_WITH_LABEL = True
SAVE_SUBGRAPHS = True

PICTURE_FORMAT = ('png', 'svg')


'''
node class, store related argument
'''
class Node(object):
    '''
    function init
    args self
    return none
    '''
    def __init__(self):
        self.idx = 0
        self.id = 0
        self.name = ''
        self.short_name = ''
        self.type = ''
        self.input_names = []
        self.inputs = []
        self.outputs = []
        self.stream = 0
        self.stream_label = ''
        self.rt_label_indexes = []
        self.rt_label_dest = []
        self.subgraph_names = []
        self.subgraphs = []
        self.owner_graph = None

        self.is_l2_first_node = False
        self.is_l2_last_node = False

        self.in_branch = False
        self.send_events = []
        self.recv_events = []
        self.send_node_names = []
        self.recv_node_names = []
        self.actived_streams = []
        self.output_offsets = []
        # 0: totally not exec, 1: before recv execed, 2: self execed
        self.is_exec = 0
        # 0: not abnormal, 1: not key abnormal, 2: key abnormal
        self.abnormal_level = 0

    '''
    function judge if event node or not
    args self
    return bool
    '''
    def has_event(self):
        return len(self.send_events) > 0 or len(self.recv_events) > 0

    '''
    function judge if active node or not
    args self
    return bool
    '''
    def is_active(self):
        return len(self.actived_streams) > 0

    '''
    function judge if label node or not
    args self
    return bool
    '''
    def is_label_like(self):
        return len(self.rt_label_indexes) != 0


'''
graph class, store related argument, including node
'''
class Graph(object):
    '''
    graph config
    '''
    class Config(object):
        def __init__(self):
            self.show_l2_tag = False

    '''
    function init
    args self
    return none
    '''
    def __init__(self):
        self.cfg = self.Config()

        self.name = ''
        self.nodes = []
        self.stream_labels = []
        self.stream_num = 0
        self.parent_node = None

        self.id_node_map = {}
        self.name_node_map = {}
        self.repeated_node_names = set()

        # 两层列表，第一层下标为stream_id，元素为stream上的node
        self.stream_nodes_all = []
        self.stream_nodes_without_events = []

        self.streams_in_branch = set()
        self.send_event_map = {}
        self.recv_event_map = {}

        # {offset: [node1, node2]}
        self.output_offset_node_map = {}

        # {streamid: [node1, node2]}
        self.stream_active_by_map = []

        self.stream_execing = []

    '''
    function build graph, fill all inner member such as event, stream and so on
    args self
    return none
    '''
    def build(self):
        for idx in range(len(self.nodes)):
            self.nodes[idx].idx = idx

        for node in self.nodes:
            self.id_node_map[node.id] = node
            if node.name not in self.name_node_map:
                self.name_node_map[node.name] = node
            elif node.name not in self.repeated_node_names:
                self.repeated_node_names.add(node.name)
                print('Warning: Node name ' + node.name + ' is repeated.')

        for node in self.nodes:
            for name, index in node.input_names:
                if name in self.name_node_map:
                    node.inputs.append((self.name_node_map[name], index))
                else:
                    print('Warning: input ' + name + ' of node ' + node.name + 'not found.')

        for node in self.nodes:
            for index, (input_node, input_output_idx) in enumerate(node.inputs):
                if input_output_idx == -1:
                    input_node.outputs.append((node, -1))
                else:
                    input_node.outputs.append((node, index))

        if len(self.nodes) > 0:
            max_stream_node = max(self.nodes, key=lambda node: node.stream)
            self.stream_num = max_stream_node.stream + 1

        self.handle_events()
        self.handle_streams()
        self.handle_labels()
        self.handle_mem_offsets()
        self.check_events()

    '''
    function merge several sub graph to a whole graph
    args [] all sub graphs
    return Graph merged graph
    '''
    @staticmethod
    def merge(graphs):
        name_to_graph = {}
        for graph in graphs:
            name_to_graph[graph.name] = graph

        for graph in graphs:
            for node in graph.nodes:
                node.owner_graph = graph
                for subgraph_name in node.subgraph_names:
                    subgraph = name_to_graph[subgraph_name]
                    node.subgraphs.append(subgraph)
                    subgraph.parent_node = node

        if len(graphs) == 1:
            merged_graph = graphs[0]
        else:
            root_graph = graphs[0]
            all_nodes = []
            candidates = root_graph.nodes
            while len(candidates) > 0:
                front = candidates.pop(0)
                all_nodes.append(front)

                subgraph_nodes = []
                for subgraph_name in front.subgraph_names:
                    subgraph = name_to_graph[subgraph_name]
                    subgraph_nodes.extend(subgraph.nodes)
                subgraph_nodes.extend(candidates)
                candidates = subgraph_nodes

            merged_graph = MergedGraph()
            merged_graph.root_graph = root_graph
            merged_graph.nodes = all_nodes

        merged_graph.build()

        return merged_graph

    '''
    function: process events info, fill inner membeer stream_nodes_all, send_event_map, recv_event_map
              remove send,recv node from inner member nodes
    args: self
    return: none
    '''
    def handle_events(self):
        # 初始化stream_nodes_all
        for stream in range(0, self.stream_num):
            self.stream_nodes_all.append([])
        for node in self.nodes:
            if node.stream >= 0:
                self.stream_nodes_all[node.stream].append(node)

        # 初始化node的send_events和recv_events成员
        for nodes_per_stream in self.stream_nodes_all:
            prev_node = None
            recv_events = []
            recv_node_names = []
            for node in nodes_per_stream:
                if node.type == 'Send':
                    event = int(node.name.split('_Send_')[1])
                    prev_node.send_events.append(event)
                    prev_node.send_node_names.append(node.name)
                elif node.type == 'Recv':
                    event = int(node.name.split('_Recv_')[1])
                    recv_events.append(event)
                    recv_node_names.append(node.name)
                else:
                    node.recv_events = recv_events
                    node.recv_node_names = recv_node_names
                    recv_events = []
                    recv_node_names = []
                    prev_node = node
            assert(len(recv_events) == 0)

        # 移除Send和Recv节点
        new_nodes = []
        for node in self.nodes:
            if node.type not in ['Send', 'Recv']:
                new_nodes.append(node)
        self.nodes = new_nodes

        # 创建<event, node>映射表
        for node in self.nodes:
            for event in node.send_events:
                self.send_event_map[event] = node
            for event in node.recv_events:
                self.recv_event_map[event] = node
                if event not in self.send_event_map:
                    print('Warning: send node for event ' + str(event) + ' not found(recv node: ' + node.name + ').')
        if len(self.send_event_map) != len(self.recv_event_map):
            print('Error: The numbers of Send and Recv do not match. (Send: ' + str(len(self.send_event_map)) + \
                  ', Recv: ' + str(len(self.recv_event_map)) + ').')

    '''
    function: process streams info,
              fill inner membeer stream_nodes_without_events, stream_labels, streams_in_branch, stream_active_by_map
    args: self
    return: none
    '''
    def handle_streams(self):
        # 如果写成： self.stream_nodes_without_events = [[]] * self.stream_num，
        # 外层列表的每个元素实际上是相同内层列表的引用，只要修改外层列表的一个元素，其他元素也会跟着变化，
        # 所以需要分别赋值
        self.stream_nodes_without_events = []
        for stream in range(0, self.stream_num):
            self.stream_nodes_without_events.append([])

        self.stream_labels = [''] * self.stream_num
        for node in self.nodes:
            if node.stream == -1:
                continue
            self.stream_nodes_without_events[node.stream].append(node)

            if node.stream_label != '':
                if self.stream_labels[node.stream] == '':
                    self.stream_labels[node.stream] = node.stream_label
                elif self.stream_labels[node.stream] != node.stream_label:
                    print('Warning: Label ' + node.stream_label + ' of node ' + node.name + \
                          ' is different from the label of the stream which it belongs(stream: ' + \
                          str(node.stream) + ').')

        for node in self.nodes:
            if (node.type == 'StreamSwitch' or (node.type == 'StreamActive' and node.in_branch)):
                for stream_id in node.actived_streams:
                    self.streams_in_branch.add(stream_id)

        for stream in range(0, self.stream_num):
            self.stream_active_by_map.append([])
        for node in self.nodes:
            for stream_id in node.actived_streams:
                self.stream_active_by_map[stream_id].append(node)

    '''
    function: process label info in node, fill rt_label_dest in node
    args: self
    return: none
    '''
    def handle_labels(self):
        idx_labelset_map = {}
        for node in self.nodes:
            if node.type in ['LabelSet']:
                assert(len(node.rt_label_indexes) == 1)
                idx_labelset_map[node.rt_label_indexes[0]] = node

        for node in self.nodes:
            if node.type in ['LabelGoto', 'LabelGotoEx', 'LabelSwitch', 'LabelSwitchByIndex']:
                for idx in node.rt_label_indexes:
                    node.rt_label_dest.append(idx_labelset_map[idx])

    '''
    function: process mem offset info, fill inner member output_offset_node_map
    args: self
    return: none
    '''
    def handle_mem_offsets(self):
        for node in self.nodes:
            for offset in node.output_offsets:
                if offset in self.output_offset_node_map:
                    self.output_offset_node_map[offset].append(node)
                else:
                    self.output_offset_node_map[offset] = [node]

    '''
    function: check event info correction, number not equal judge incorrect
    args: self
    return: none
    '''
    def check_events(self):
        # 检查Send Event与RecvEvent是否匹配
        all_send_events = set()
        all_recv_events = set()
        for node in self.nodes:
            for event in node.send_events:
                all_send_events.add(event)
            for event in node.recv_events:
                all_recv_events.add(event)
        missing_send_events = all_recv_events - all_send_events
        missing_recv_events = all_send_events - all_recv_events
        if len(missing_send_events) > 0:
            msg = 'Warning: missing send events(may cause deadlock):' + num_list_to_str(missing_send_events)
            print(msg)
        if len(missing_recv_events) > 0:
            msg = 'Warning: missing recv events:' + num_list_to_str(missing_recv_events)
            print(msg)

    '''
    function: analyze exec record, mark if node is execed
    args: self
    args: {} exec_record, content like { streamid: last_exec_node_name }
    return: int
    '''
    def mark_is_exec(self, exec_record):
        for stream_id, last_exec_node_name in exec_record.items():
            is_reach_exec_node = False
            for node in self.stream_nodes_without_events[int(stream_id)]:
                if last_exec_node_name in node.recv_node_names:
                    node.is_exec = 1
                    is_reach_exec_node = True
                    break
                elif last_exec_node_name == node.name:
                    node.is_exec = 2
                    is_reach_exec_node = True
                    break
                else:
                    node.is_exec = 2
            if is_reach_exec_node == False:
                msg = 'Warning: streamid:' + stream_id + ' last_exec_node:' + last_exec_node_name + \
                      ' not find in dump graph, maybe record file and dump graph file not match'
                print(msg)
                return -1
        return 0

    '''
    function: analyze exec record, mark if node is abnormal from exec info and event active relation
    args: self
    args: {} exec_record, content like { streamid: last_exec_node_name }
    return: None
    '''
    def mark_abnormal(self, exec_record):
        abnormal_active_node_set = set()
        for stream_id, last_exec_node_name in exec_record.items():
            for node in self.stream_nodes_without_events[int(stream_id)]:
                if last_exec_node_name == node.name:
                    node.abnormal_level = 2
                    msg = 'Message: streamid:' + stream_id + ' last_exec_node:' + last_exec_node_name + \
                          ' not event wait task, but still running'
                    print(msg)
                    break
                if last_exec_node_name in node.recv_node_names:
                    event = int(last_exec_node_name.split('_Recv_')[1])
                    send_node = self.send_event_map[event]
                    if send_node.is_exec == 2:
                        node.abnormal_level = 2
                        msg = 'Message: streamid:' + stream_id + ' last_exec_node:' + last_exec_node_name + \
                              ', it\'s send node:' + send_node.name + ' is executed'
                        print(msg)
                    else:
                        send_stream_id = send_node.stream
                        if str(send_stream_id) not in exec_record.keys():
                            for active_node in self.stream_active_by_map[send_stream_id]:
                                msg = 'Message: streamid:' + stream_id + ' last_exec_node:' + last_exec_node_name + \
                                      ', the streamid:' + str(send_stream_id) + ' it\'s send node:' + send_node.name + \
                                      ' at, is not active.' + 'should have been actived by node:' + active_node.name
                                print(msg)
                                active_node.abnormal_level = 2
                                send_node.abnormal_level = 1
                                abnormal_active_node_set.add(active_node)
                        else:
                            send_node.abnormal_level = 1
                    break

        next_round = abnormal_active_node_set
        while len(next_round) != 0:
            abnormal_active_node_set = next_round
            next_round = set()
            for abnormal_active_node in abnormal_active_node_set:
                curr_stream_id = abnormal_active_node.stream
                if str(curr_stream_id) in exec_record.keys():
                    abnormal_active_node.abnormal_level = 1
                elif curr_stream_id not in self.streams_in_branch or \
                     self.stream_labels[curr_stream_id] == 'Node_Output_IteratorCtrl_StreamSwitch_StreamActive' or \
                     abnormal_active_node.type == 'StreamSwitch':
                    abnormal_active_node.abnormal_level = 2
                else:
                    for pre_active_node in self.stream_active_by_map[curr_stream_id]:
                        abnormal_active_node.abnormal_level = 1
                        next_round.add(pre_active_node)


    '''
    function: process exec_record data, mark is_exec and is abnnormal info in all nodes
    args: self
    args: {} exec_record, content like { streamid: last_exec_node_name }
    return: None
    '''
    def run_exec_record(self, exec_record):
        self.stream_execing = exec_record.keys()
        self.mark_is_exec(exec_record)
        self.mark_abnormal(exec_record)

    '''
    function: write graph info to file
    args: self
    args: string file_basename, target file name
    return: None
    '''
    def dump_text(self, file_basename):
        dump_file = file_basename + '.dump.txt'
        with open(dump_file, 'w') as f:
            self.dump_text_to_opened_file(f)
        print(dump_file + ' is created.')

    '''
    function: write graph info to file
    args: self
    args: f, object opened file
    return: None
    '''
    def dump_text_to_opened_file(self, f):
        if DUMP_TEXT_NODES:
            if self.name != '':
                f.write('graph: ' + self.name + '\n\n')

            for node in self.nodes:
                f.write('id: ' + str(node.id) + '\n')
                f.write('name: ' + node.name + '\n')
                f.write('type: ' + node.type + '\n')

                if node.stream_label != '':
                    f.write('stream: ' + str(node.stream) + ' (stream_label: ' + node.stream_label + ')\n')
                else:
                    f.write('stream: ' + str(node.stream) + '\n')

                if len(node.actived_streams) > 0:
                    f.write('actived_streams:' + num_list_to_str(node.actived_streams) + '\n')

                if len(node.rt_label_indexes) > 0:
                    f.write('label_indexes:' + num_list_to_str(node.rt_label_indexes) + '\n')

                if node.owner_graph.parent_node is not None:
                    f.write('owner_graph: ' + node.owner_graph.name + '\n')

                for subgraph in node.subgraph_names:
                    f.write('subgraph: ' + subgraph + '\n')

                if self.cfg.show_l2_tag:
                    if node.is_l2_first_node:
                        f.write('is_first_node: true\n')
                    if node.is_l2_last_node:
                        f.write('is_last_node: true\n')

                # predecessors
                for input_node, index in node.inputs:
                    label_str = ''
                    if (input_node.stream_label != ''):
                        label_str = ', label:' + input_node.stream_label
                    f.write('pred: ' + input_node.name + ':' + str(index) + ' (' + input_node.type + \
                            ', id:' + str(input_node.id) + ', stream:' + str(input_node.stream) + label_str + ')\n')

                # successors
                for output_node, index in node.outputs:
                    label_str = ''
                    if (output_node.stream_label != ''):
                        label_str = ', label:' + output_node.stream_label
                    f.write('succ: ' + output_node.name + ':' + str(index) + ' (' + output_node.type + \
                            ', id:' + str(output_node.id) + ', stream:' + str(output_node.stream) + label_str + ')\n')

                for offset in node.output_offsets:
                    f.write('output_offset: ' + str(offset) + '\n')

                f.write('\n')

        # 打印控制算子与子图间的关系
        for node in self.nodes:
            if len(node.subgraphs) > 0:
                f.write('Node ' + node.name + ' has ' + str(len(node.subgraphs)) + ' subgraphs:')
                for subgraph in node.subgraphs:
                    f.write(' ' + subgraph.name)
                f.write('\n\n')

        # 打印stream和node的关系
        if DUMP_TEXT_STREAM_NODES:
            for stream_id, nodes in enumerate(self.stream_nodes_without_events):
                stream_str = str(len(nodes)) + ' nodes in stream ' + str(stream_id)
                if self.stream_labels[stream_id] != '':
                    stream_str += '(' + self.stream_labels[stream_id] + ')'
                stream_str += ':'

                for node in nodes:
                    stream_str = stream_str + ' ' + node.name + '(' + str(node.id) + ')'
                f.write(stream_str + '\n')

            f.write('\n')

        # 打印激活关系
        if DUMP_TEXT_STREAM_ACTIVED_STREAMS:
            for node in self.nodes:
                if len(node.actived_streams) > 0:
                    f.write('Streams actived by ' + node.name + '(stream ' + str(node.stream) + '):')
                    f.write(num_list_to_str(node.actived_streams) + '\n')

        # 打印输出数据offset与算子间的关系
        if DUMP_TEXT_MEMORY:
            f.write('\n')
            for offset, nodes in self.output_offset_node_map.items():
                streams_tmp = set()
                for node in nodes:
                    if node.stream != -1:
                        streams_tmp.add(node.stream)

                if len(nodes) > 1 and len(streams_tmp) > 1:
                    f.write('output ' + str(offset) + ':' + '\n')
                    for node in nodes:
                        f.write('  stream ' + str(node.stream) + ', id ' + str(node.id) + ': ' + node.name + '\n')


'''
MergedGraph class, store multi graph info
'''
class MergedGraph(Graph):

    def __init__(self):
        super(MergedGraph, self).__init__()
        self.root_graph = None


'''
Parser class, tool class to parse input file, such as graph file and exec_record file
'''
class Parser(object):
    '''
    function init
    args self
    return none
    '''
    def __init__(self):
        pass

    '''
    function parse graph file info to class graph
    args self
    args string file, graph file name
    return none
    '''
    def parse(self, file):
        (_, filename) = os.path.split(file)
        if filename.startswith('ge_proto_'):
            is_onnx_file = False
        elif filename.startswith('ge_onnx_'):
            is_onnx_file = True
        else:
            print('Warning: ' + file + ' does not start with "ge_proto_" or "ge_onnx_".')
            return None

        # 逐行读取文件
        all_lines = []
        with open(file, 'r', encoding="gbk") as f:
            for line in f:
                all_lines.append(line)

        graph_lines = self.split_lines(all_lines)
        all_lines = None

        graphs = []
        for lines in graph_lines:
            graph = Graph()
            if is_onnx_file:
                self.parse_onnx(lines, graph)
            else:
                self.parse_proto(lines, graph)
            graphs.append(graph)

        if len(graphs) > 1:
            print(file + ' contains ' + str(len(graphs)) + ' graphs.')

        return graphs

    '''
    function parse exec record file info to map data
    args self
    args string exec_record_file, exec_record file name
    args int device_id, device_id which task executed on
    args Graph graph, graph data after parsed
    return none
    '''
    def parse_exec_record_file(self, exec_record_file, device_id, graph):
        # parse
        # [[node1, node2], [node1, node2]]
        exec_records = []
        in_target_record = False
        with open(exec_record_file, 'r', encoding="gbk") as f:
            for line in f:
                # split for several exec record
                if line.startswith('Device['):
                    in_target_record = False
                    if line.startswith('Device[' + str(device_id) + ']'):
                        in_target_record = True
                        exec_records.append([])

                if 'streamId' in line and in_target_record:
                    tag_info_split = line.split(',')[3].split('=')
                    if len(tag_info_split) == 2:
                        exec_records[len(exec_records) - 1].append(tag_info_split[1].strip().strip('.'))

        # check
        no_content = True
        for record in exec_records:
            if len(record) != 0:
                no_content = False
                break

        if no_content:
            msg = 'Message: exec_record file parse out no content. Possible Reason:\n' + \
                  '    1. input file invalid.\n' + \
                  '    2. device id invalid, no model executing on.\n' + \
                  '    3. not block on execute stage, maybe block on compile stage.\n'
            print(msg)
            exit()

        for record in exec_records:
            if record != exec_records[0]:
                msg = 'Message: several exec records not equal, means device model is stilling running, not blocked\n'
                print(msg)
                exit()

        # relate to graph
        # { stream_id1 : node_name1, stream_id2 : node_name2 }
        graph_exec_record = {}
        for node_name in exec_records[0]:
            if node_name not in graph.name_node_map.keys():
                msg = 'Message: node: ' + node_name + \
                      ' not found in graph, the exec_record not match to graph file. please check\n'
                print(msg)
                exit()
            else:
                graph_exec_record[str(graph.name_node_map[node_name].stream)] = node_name

        return graph_exec_record

    '''
    function split all graph file line to several graph info
    args self
    args [] all_lines, all graph file
    return none
    '''
    def split_lines(self, all_lines):
        graph_lines = []

        is_graph_line = False
        for line in all_lines:
            if is_graph_line:
                graph_lines[len(graph_lines) - 1].append(line)
                if line.startswith('}'):
                    is_graph_line = False
            elif line.startswith('graph {'):
                graph_lines.append([line])
                is_graph_line = True

        return graph_lines

    '''
    function parse ge_proto graph file to class Graph data
    args self
    args [] lines, single graph data all lines from file
    args Graph graph, output args, will be filled when function called
    return none
    '''
    def parse_proto(self, lines, graph):
        """
        proto格式：
        ^graph {
        ^  op {
        ^    name: "Cast_31"
        ^    name: "_Send_0"
        ^    name: "_Recv_0"
        ^    type: "Mul"
        ^    id: 175
        ^    stream_id: 7
        ^    attr {
        ^      key: "_stream_label"
        ^      value {
        ^        s: "IteratorOpPass_0"
        ^      }
        ^    }
        ^    attr {
        ^      key: "active_stream_list"
        ^      value {
        ^        list {
        ^          i: 3
        ^          val_type: VT_LIST_INT
        ^        }
        ^      }
        ^    }
        ^  }
        ^}
        """

        node = None
        stream_label_start = False
        active_streams_start = False
        label_switch_index_start = False
        label_switch_list_start = False
        for line in lines:
            if line.startswith('  name: "'):
                graph.name = self.get_value(line)
            elif line.startswith('  op {'):
                if node is not None:
                    graph.nodes.append(node)
                node = Node()
            elif line.startswith('    name:'):
                node.name = self.get_value(line)
                splited_name = node.name.split('/')
                node.short_name = splited_name[len(splited_name) - 1]

            elif line.startswith('    type:'):
                node.type = self.get_value(line)
            elif line.startswith('    id:'):
                node.id = int(self.get_value(line))
            elif line.startswith('    input:'):
                value = self.get_value(line)
                if value != '':
                    input_name, input_output_index = value.split(':')
                    node.input_names.append((input_name, int(input_output_index)))
            elif line.startswith('    stream_id:'):
                node.stream = int(self.get_value(line))
            elif line.startswith('    subgraph_name:'):
                node.subgraph_names.append(self.get_value(line))
            elif line.startswith('      key: "_stream_label"'):
                stream_label_start = True
            elif line.startswith('      key: "active_stream_list"'):
                active_streams_start = True
            elif line.startswith('      key: "_switch_branch_node_label"'):
                node.in_branch = True
            elif line.startswith('      key: "_label_switch_index"'):
                label_switch_index_start = True
            elif line.startswith('      key: "_label_switch_list"'):
                label_switch_list_start = True
            elif line.startswith('      key: "is_first_node"'):
                node.is_l2_first_node = True
            elif line.startswith('      key: "is_last_node"'):
                node.is_l2_last_node = True
            elif line.startswith('        i: '):
                if label_switch_index_start:
                    node.rt_label_indexes.append(int(self.get_value(line)))
                    label_switch_index_start = False
            elif line.startswith('        s: '):
                if stream_label_start:
                    node.stream_label = self.get_value(line)
                    stream_label_start = False
            elif line.startswith('          i: '):
                if active_streams_start:
                    node.actived_streams.append(int(self.get_value(line)))
                elif label_switch_list_start:
                    node.rt_label_indexes.append(int(self.get_value(line)))
            elif line.startswith('          val_type: VT_LIST_INT'):
                active_streams_start = False
                label_switch_list_start = False
            elif line.startswith('    output_i:'):
                node.output_offsets.append(int(self.get_value(line)))

        if node is not None:
            graph.nodes.append(node)

    '''
    function parse ge_proto graph file to class Graph data
    args self
    args [] lines, single graph data all lines from file
    args Graph graph, output args, will be filled when function called
    return none
    '''
    def parse_onnx(self, lines, graph):
        """
        onnx格式：
        ^graph {
        ^  node {
        ^    name: "ReLU-op122"
        ^    name: "_Send_0"
        ^    name: "_Recv_0"
        ^    op_type: "ge:Relu"
        ^    attribute {
        ^      name: "id"
        ^      i: 1741
        ^      type: INT
        ^    }
        ^    attribute {
        ^      name: "stream_id"
        ^      i: 5
        ^      type: INT
        ^    }
        ^    attribute {
        ^      name: "_stream_label"
        ^      s: "IteratorOpPass_0"
        ^      type: STRING
        ^    }
        ^    attribute {
        ^      name: "active_stream_list"
        ^      ints: 1
        ^      ints: 2
        ^      ints: 4
        ^      ints: 6
        ^      ints: 7
        ^      ints: 8
        ^      ints: 9
        ^      ints: 10
        ^      type: INTS
        ^    }
        ^  }
        ^}
        """

        node = None
        id_start = False
        stream_id_start = False
        stream_label_start = False
        active_streams_start = False
        output_offset_start = False
        for line in lines:
            if line.startswith('  name: "'):
                graph.name = self.get_value(line)
            elif line.startswith('  node {'):
                if node is not None:
                    graph.nodes.append(node)
                node = Node()
            elif line.startswith('    name:'):
                node.name = self.get_value(line)
                splited_name = node.name.split('/')
                node.short_name = splited_name[len(splited_name) - 1]
            elif line.startswith('    op_type:'):
                node.type = self.get_value(line)
                node.type = node.type.split('ge:')[1]
            elif line.startswith('      name: "id"'):
                id_start = True
            elif line.startswith('    input:'):
                value = self.get_value(line)
                if value != '':
                    input_name, input_output_index = value.split(':')
                    node.input_names.append((input_name, int(input_output_index)))
            elif line.startswith('      name: "stream_id"'):
                stream_id_start = True
            elif line.startswith('      name: "_stream_label"'):
                stream_label_start = True
            elif line.startswith('      name: "active_stream_list"'):
                active_streams_start = True
            elif line.startswith('      name: "_switch_branch_node_label"'):
                node.in_branch = True
            elif line.startswith('      name: "output_i"'):
                output_offset_start = True
            elif line.startswith('      s:'):
                if stream_label_start:
                    node.stream_label = self.get_value(line)
                    stream_label_start = False
            elif line.startswith('      ints:'):
                if active_streams_start:
                    node.actived_streams.append(int(self.get_value(line)))
                elif output_offset_start:
                    node.output_offsets.append(int(self.get_value(line)))
            elif line.startswith('      type: INTS'):
                active_streams_start = False
                output_offset_start = False
            elif line.startswith('      i:'):
                if id_start:
                    node.id = int(self.get_value(line))
                elif stream_id_start:
                    node.stream = int(self.get_value(line))
            elif line.startswith('      type: INT'):
                if id_start:
                    id_start = False
                elif stream_id_start:
                    stream_id_start = False

        if node is not None:
            graph.nodes.append(node)

    '''
    function to split line with :, get second info and strip
    args self
    args string str, line to be processed
    return none
    '''
    def get_value(self, str):
        _, value = str.split(':', 1)
        return value.strip().replace('"', '')


'''
Saver class, tool class to save graph data to file formated by graphviz, and generate corresponding graph
'''
class Saver(object):
    '''
    Saver config
    '''
    class Config(object):
        def __init__(self):
            self.save_graph = False
            self.show_all_nodes = False
            self.lighted_nodes = None
            self.start_node = None
            self.end_node = None
            self.light_subgraphs = False
            self.show_l2_tag = False

    '''
    function init
    args self
    args Graph graph, graph data after
    return none
    '''
    def __init__(self, graph):
        self.graph = graph
        self.cfg = self.Config()

        self.visible_nodes = set()
        self.hidden_nodes = set()
        self.lighted_nodes = set()

        self.start_node_id = -1
        self.end_node_id = sys.maxsize

        self.bgcolors = ['aliceblue', 'antiquewhite', 'antiquewhite3', 'antiquewhite4', 'aquamarine', 'aquamarine4', \
                         'azure3', 'cadetblue', 'cadetblue4', 'chocolate', 'coral', 'cornflowerblue', 'cyan', \
                         'darkgoldenrod', 'darkgoldenrod2', 'darkolivegreen1', 'darksalmon', 'dodgerblue']

    '''
    function save function entrance
    args self
    return none
    '''
    def save(self, filename):
        self.select_displayed_nodes()

        self.save_sequence(filename + '.sequence')
        self.save_streams(filename + '.streams')
        self.save_subgraphs(filename + '.subgraphs')
        if self.cfg.save_graph:
            self.save_graph(filename + '.graph')

    '''
    function analyze related config, judge which node will be displayed
    args self
    return none
    '''
    def select_displayed_nodes(self):
        # 通过--light-nodes参数指定要显示的算子
        for node in self.cfg.light_nodes.split(','):
            if node.isdigit():
                self.lighted_nodes.add(self.graph.id_node_map[int(node)])
            elif node != '':
                self.lighted_nodes.add(self.graph.name_node_map[node])

        # --light-nodes相关算子的前驱也显示
        for node in self.lighted_nodes:
            self.visible_nodes.add(node)
            for intpu_node, _ in node.inputs:
                self.visible_nodes.add(intpu_node)

        # 确定通过--start-node和--end-node指定的算子显示范围
        if self.cfg.start_node.isdigit():
            self.start_node_id = int(self.cfg.start_node)
        elif self.cfg.start_node != '':
            self.start_node_id = self.graph.name_node_map[self.cfg.start_node].id
        if self.cfg.end_node.isdigit():
            self.end_node_id = int(self.cfg.end_node)
        elif self.cfg.end_node != '':
            self.end_node_id = self.graph.name_node_map[self.cfg.end_node].id

        for node in self.graph.nodes:
            if (node.id < self.start_node_id or node.id > self.end_node_id):
                self.hidden_nodes.add(node)

        # 通过--light-nodes指定的算子也显示
        self.hidden_nodes = self.hidden_nodes - self.lighted_nodes

        # 未隐藏算子的前驱和前面的同步结点也显示
        for node in self.graph.nodes:
            if node not in self.hidden_nodes:
                for intpu_node, _ in node.inputs:
                    if intpu_node in self.hidden_nodes:
                        self.hidden_nodes.remove(intpu_node)
                for event in node.recv_events:
                    send_node = self.graph.send_event_map[event]
                    if send_node in self.hidden_nodes:
                        self.hidden_nodes.remove(send_node)

    '''
    function save stream sequence file entrance
    args self
    args string filename, target file name
    return none
    '''
    def save_sequence(self, filename):
        if not SAVE_SEQUENCE:
            return

        dot_file = filename + '.dot'
        with open(dot_file, 'w') as f:
            f.write('digraph sequence {\n')
            f.write('rankdir = "LR";\n')
            f.write('node[shape = "plaintext", width = 0, height = 0];\n')
            f.write('edge[arrowhead = "none", style = "dashed"];\n\n')
            self.write_streams(f)
            self.write_edges(f)
            self.write_actives(f)
            f.write('}\n')
        print(dot_file + ' is created.')
        self.save_picture(filename)

    '''
    function save stream active file entrance
    args self
    args string filename, target file name
    return none
    '''
    def save_streams(self, filename):
        """
        ^ digraph actives {
        ^ node[shape=record];
        ^ Stream0[label=<{Stream 0|3(1+2) nodes|<i>IteratorOpPass_1</i>}>]
        ^ Stream1[label=<{Stream 1|4(1+3) nodes|<i>IteratorOpPass_0</i>}>]
        ^ ...
        ^ Stream6[label=<{Stream 6|6(2+4) nodes}>]
        ^ Stream7[label=<{Stream 7|7(3+4) nodes}>]
        ^ Stream2 -> Stream3
        ^ Stream3 -> Stream0
        ^ ...
        ^ }
        """
        if not SAVE_STREAMS:
            return

        dot_file = filename + '.dot'
        with open(dot_file, 'w') as f:
            f.write('digraph actives {\n')
            f.write('node[shape=record];\n')
            for stream_id, stream_label in enumerate(self.graph.stream_labels):
                all_node_num = len(self.graph.stream_nodes_all[stream_id])
                node_num_without_event = len(self.graph.stream_nodes_without_events[stream_id])
                stream_str = 'Stream ' + str(stream_id)
                stream_str += '|' + str(all_node_num) + '(' + str(node_num_without_event) + '+' + \
                              str(all_node_num - node_num_without_event) + ') nodes'
                if SAVE_STREAMS_WITH_LABEL and stream_label != '':
                    stream_str += '|<i>' + stream_label + '</i>'
                f.write('Stream' + str(stream_id) + '[label=<{' + stream_str + '}>')
                if stream_id in self.graph.streams_in_branch:
                    f.write(', color=blue')
                if str(stream_id) in self.graph.stream_execing:
                    f.write(', fontcolor=green')
                f.write(']\n')

            for node in self.graph.nodes:
                if len(node.actived_streams) > 0:
                    for actived_stream in node.actived_streams:
                        f.write('Stream' + str(node.stream) + ' -> ' + 'Stream' + str(actived_stream) + '\n')
            f.write('}\n')
        print(dot_file + ' is created.')
        self.save_picture(filename)

    '''
    function save subgraph info entrance
    args self
    args string filename, target file name
    return none
    '''
    def save_subgraphs(self, filename):
        if not SAVE_SUBGRAPHS or not isinstance(self.graph, MergedGraph):
            return

        dot_file = filename + '.dot'
        with open(dot_file, 'w') as f:
            root_graph = self.graph.root_graph
            f.write('digraph subgraphs {\n')
            f.write('label="' + root_graph.name + '"\n')
            subgraph_idx = 0
            for node in root_graph.nodes:
                if len(node.subgraphs) > 0:
                    self.draw_ctrl_node(f, node, subgraph_idx)
            f.write('}\n')
        print(dot_file + ' is created.')
        self.save_picture(filename)

    '''
    function save subgraph info file
    args self
    args string filename, target file name
    return none
    '''
    def draw_ctrl_node(self, f, node, subgraph_idx):
        f.write('subgraph cluster_' + str(subgraph_idx) + ' {\n')
        f.write('label="' + node.name + '"\n')
        f.write('bgcolor=' + self.bgcolors[subgraph_idx % len(self.bgcolors)] + '\n')
        subgraph_idx = subgraph_idx + 1

        for subgraph in node.subgraphs:
            f.write('subgraph cluster_' + str(subgraph_idx) + ' {\n')
            f.write('bgcolor=' + self.bgcolors[subgraph_idx % len(self.bgcolors)] + '\n')
            subgraph_idx = subgraph_idx + 1

            ctrl_node_num = 0
            for sub_node in subgraph.nodes:
                if len(sub_node.subgraphs) > 0:
                    ctrl_node_num = ctrl_node_num + 1
                    self.draw_ctrl_node(f, sub_node, subgraph_idx)
            if ctrl_node_num == 0:
                f.write('label=""\n')
                f.write('"' + subgraph.name + '" [shape=plaintext]\n')
            else:
                f.write('label="' + subgraph.name + '"\n')

            f.write('}\n')

        f.write('}\n')

    '''
    function save graph info file
    args self
    args string filename, target file name
    return none
    '''
    def save_graph(self, filename):
        dump_nodes = []
        for node in self.graph.nodes:
            if node.id >= self.start_node_id and node.id <= self.end_node_id:
                dump_nodes.append(node)

        onnx_file = filename + '.pbtxt'
        with open(onnx_file, 'w') as f:
            node_output_idx = {}
            for node in dump_nodes:
                node_output_idx[node] = set()
            for node in dump_nodes:
                for input_node, index in node.inputs:
                    if input_node in dump_nodes:
                        node_output_idx[input_node].add(index)
            f.write('graph {\n')
            for node in dump_nodes:
                f.write('  node {\n')
                f.write('    name: "' + node.name + '"\n')
                f.write('    op_type: "' + node.type + '"\n')
                f.write('    attribute {\n')
                f.write('      name: "id"\n')
                f.write('      i: ' + str(node.id) + '\n')
                f.write('      type: INT\n')
                f.write('    }\n')
                for input_node, index in node.inputs:
                    if input_node in dump_nodes:
                        f.write('    input: "' + input_node.name + ':' + str(index) + '"\n')
                for index in node_output_idx[node]:
                    f.write('    output: "' + node.name + ':' + str(index) + '"\n')
                f.write('  }\n')
            f.write('}\n')
        print(onnx_file + ' is created.')

        dot_file = filename + '.dot'
        with open(dot_file, 'w') as f:
            f.write('digraph g {')
            if True:
                # 打印拓扑序上start和end之间所有结点
                for node in dump_nodes:
                    f.write(self.dot_name(node) + \
                            '[label="' + node.short_name + '\\n' + node.type + '\\n' + str(node.id) + '"]\n')
                for node in dump_nodes:
                    for input_node, index in node.inputs:
                        if input_node in dump_nodes:
                            f.write(self.dot_name(input_node) + '->' + self.dot_name(node))
                            if index == -1:
                                f.write('[style = "dashed"]')
                            f.write('\n')
            else:
                # 打印start_node及所有后继（仅看数据边）
                start_node = self.graph.id_node_map[self.graph.start_node_id]
                candidate_nodes = collections.deque([start_node])
                while len(candidate_nodes) > 0:
                    node = candidate_nodes.popleft()
                    f.write(self.dot_name(node) + \
                            '[label="' + node.short_name + '\\n' + node.type + '\\n' + str(node.id) + '"]\n')
                    for output_node, index in node.outputs:
                        if index != -1:
                            f.write(self.dot_name(node) + '->' + self.dot_name(output_node) + '\n')
                            candidate_nodes.append(output_node)
            f.write('}')

        print(dot_file + ' is created.')
        self.save_picture(filename)

    '''
    function tranform dot file to picture file
    args self
    args string filename, target file name
    return none
    '''
    def save_picture(self, filename):
        if not SAVE_PICTURE:
            return

        dot_file = filename + '.dot'
        for one_format in PICTURE_FORMAT:
            picture_file = filename + '.' + one_format
            os.system('dot -T ' + one_format + ' -o ' + picture_file + ' ' + dot_file)
            print(picture_file + ' is created.')

    '''
    function tranform dot file to picture file
    args self
    args string filename, target file name
    return bool
    '''
    def is_node_displayed(self, node, stream_nodes):
        if node in self.hidden_nodes:
            return False
        return (self.cfg.show_all_nodes or node.abnormal_level != 0 or
                node == stream_nodes[0] or node == stream_nodes[len(stream_nodes) - 1] or
                node.has_event() or node.is_active() or node.is_label_like() or len(node.subgraphs) > 0 or
                node in self.visible_nodes or
                (self.cfg.show_l2_tag and (node.is_l2_first_node or node.is_l2_last_node)))

    '''
    function get all stream will be displayed
    args self
    return [int] streams
    '''
    def get_displayed_streams(self):
        streams = []
        for stream_id, nodes in enumerate(self.graph.stream_nodes_without_events):
            for node in nodes:
                if self.is_node_displayed(node, nodes):
                    streams.append(stream_id)
                    break
        return streams

    '''
    function write stream sequeance info to file with dot format
    args self
    args object f, opened target file to write
    return None
    '''
    def write_streams(self, f):
        subgraph_bgcolor_map = {}
        if self.cfg.light_subgraphs:
            for node in self.graph.nodes:
                for subgraph_name in node.subgraph_names:
                    subgraph_bgcolor_map[subgraph_name] = ''
            for idx, subgraph_name in enumerate(subgraph_bgcolor_map):
                subgraph_bgcolor_map[subgraph_name] = self.bgcolors[idx % len(self.bgcolors)]

        displayed_streams = self.get_displayed_streams()

        tmp_node_id = 0
        for stream_id, nodes in enumerate(self.graph.stream_nodes_without_events):
            if stream_id not in displayed_streams:
                continue

            node_dot_ids = []
            skipped_nodes = []

            all_node_num = len(self.graph.stream_nodes_all[stream_id])
            node_num_without_event = len(self.graph.stream_nodes_without_events[stream_id])

            stream_str = '<b>Stream ' + str(stream_id) + '</b>'
            stream_str += '|' + str(all_node_num) + '(' + str(node_num_without_event) + '+' \
                          + str(all_node_num - node_num_without_event) + ') nodes'
            if self.graph.stream_labels[stream_id] != '':
                stream_str += '|<i>Label: ' + self.graph.stream_labels[stream_id] + '</i>'

            color = ''
            if stream_id in self.graph.streams_in_branch:
                color = ', color="blue"'

            # {
            # rank="same";
            # edge[style="solid", penwidth=2];
            # Stream0[label=<<b>Stream 0</b>|3(1+2) nodes|<i>Label: IteratorOpPass_1</i>>, shape="record"];
            # End0[shape="point", width=0.1, height=0.1];
            f.write('{\n')
            f.write('rank="same";\n')
            f.write('edge[style="solid", penwidth=2' + color + '];\n')
            f.write('Stream' + str(stream_id) + '[label=<' + stream_str + '>, shape="record"' + color)

            if str(stream_id) in self.graph.stream_execing:
                f.write(', fontcolor=green];\n')
            else:
                f.write('];\n')

            f.write('End' + str(stream_id) + '[shape="point", width=0.1, height=0.1];\n')
            for node in nodes:
                if self.is_node_displayed(node, nodes):
                    if len(skipped_nodes) > 0:
                        # TN13[label="(151 nodes)"];
                        node_dot_ids.append('TN' + str(tmp_node_id))
                        f.write('TN' + str(tmp_node_id) + '[label="(' + str(len(skipped_nodes)) + ' nodes)"')

                        if node.is_exec != 0:
                            f.write(', fontcolor="green"')

                        if self.cfg.light_subgraphs:
                            node_subgraphs = set()
                            for skipped_node in skipped_nodes:
                                node_subgraphs.add(skipped_node.owner_graph)
                            if len(node_subgraphs) == 1 and skipped_nodes[0].owner_graph.name in subgraph_bgcolor_map:
                                f.write(', fillcolor=' + subgraph_bgcolor_map[skipped_nodes[0].owner_graph.name] + \
                                        ', style=filled')

                        f.write('];\n')
                        tmp_node_id = tmp_node_id + 1
                        skipped_nodes = []

                    # S12N1629[label=<Sqrt_1<br/>(id: 1629)>];
                    # S3N626[label=<IteratorV2_IteratorCtrl_StreamSwitch_StreamActive<br/>
                    #        (id: 626)<br/>(active streams: 0)>, fontcolor="red"];
                    # S10N926[label=<<u><b>Sum</b></u><br/>(id: 926)>, fontcolor="green"];
                    node_dot_ids.append(self.dot_name(node))
                    f.write(self.dot_name(node))

                    f.write('[label=<')
                    if node in self.lighted_nodes or node.abnormal_level == 2:
                        f.write('<u><b>' + node.short_name + '</b></u>')
                    else:
                        f.write(node.short_name)
                    f.write('<br/>(id: ' + str(node.id) + ')')
                    if len(node.actived_streams) > 0:
                        f.write('<br/>(active streams:' + num_list_to_str(node.actived_streams) + ')')
                    if len(node.rt_label_indexes) > 0:
                        f.write('<br/>(labels:' + num_list_to_str(node.rt_label_indexes) + ')')
                    if self.cfg.show_l2_tag:
                        if node.is_l2_first_node:
                            f.write('<br/>(is_first_node: true)')
                        if node.is_l2_last_node:
                            f.write('<br/>(is_last_node: true)')
                    f.write('>')

                    if node.abnormal_level == 2:
                        f.write(', fontcolor="brown", fontsize=20, shape="record", style="filled", \
                                fillcolor="darkorange"')
                    elif node.abnormal_level == 1:
                        f.write(', fontcolor="red", color="gold"')
                    elif node.is_exec == 2:
                        f.write(', fontcolor="green"')
                    #elif node in self.lighted_nodes:
                        #f.write(', fontcolor="forestgreen"')
                    #elif node in self.visible_nodes:
                        #f.write(', fontcolor="forestgreen"')
                    elif len(node.actived_streams) > 0:
                        f.write(', fontcolor="blue"')
                    elif self.cfg.show_l2_tag and (node.is_l2_first_node or node.is_l2_last_node):
                        f.write(', fontcolor="green"')

                    if node.owner_graph.name in subgraph_bgcolor_map:
                        f.write(', fillcolor=' + subgraph_bgcolor_map[node.owner_graph.name] + ', style=filled')

                    f.write('];\n')
                else:
                    skipped_nodes.append(node)

            if len(skipped_nodes) > 0:
                # TN13[label="(151 nodes)"];
                node_dot_ids.append('TN' + str(tmp_node_id))
                f.write('TN' + str(tmp_node_id) + '[label="(' + str(len(skipped_nodes)) + ' nodes)"];\n')
                tmp_node_id = tmp_node_id + 1

            # Stream8 -> TN2 -> N252 -> TN3 -> N286 -> TN4 -> N533 -> End8;
            f.write('Stream' + str(stream_id))
            for node_dot_id in node_dot_ids:
                f.write(' -> ' + node_dot_id)
            f.write(' -> End' + str(stream_id) + ';\n')

            f.write('}\n')

        if len(displayed_streams) > 1:
            f.write('Stream' + str(displayed_streams[0]))
            for index in range(1, len(displayed_streams)):
                f.write(' -> Stream' + str(displayed_streams[index]))
            f.write(' [color="white"];\n\n')

    '''
    function write stream sequence info to file with dot format, focus on event info
    args self
    args object f, opened target file to write
    return None
    '''
    def write_edges(self, f):
        # for node in self.graph.nodes:
        #     for label_dest in node.rt_label_dest:
        #         f.write(self.dot_name(node) + ' -> ' + self.dot_name(label_dest))
        #         f.write(' [label="Label ' + str(label_dest.rt_label_indexes[0]) + '", arrowhead="normal"];\n')

        for node in self.graph.nodes:
            for event in node.send_events:
                if event not in self.graph.recv_event_map:
                    print('ERROR: event ' + str(event) +' was not found in recv_event_map.')
                    continue

                recv_node = self.graph.recv_event_map[event]
                if node in self.hidden_nodes or recv_node in self.hidden_nodes:
                    continue

                # N607 -> N620 [label="Event 7", arrowhead="normal"];
                f.write(self.dot_name(node) + ' -> ' + self.dot_name(recv_node))
                f.write(' [label="Event ' + str(event) + '", arrowhead="normal"')
                if node.abnormal_level != 0:
                    f.write(', color=red')
                f.write('];\n')

    '''
    function write stream sequence info to file with dot format, focus on active info
    args self
    args object f, opened target file to write
    return None
    '''
    def write_actives(self, f):
        # 打印流间激活关系
        f.write('\n{\n')
        for node in self.graph.nodes:
            color = ''
            fontcolor = ''
            if node.type == 'StreamSwitch':
                color = ', color="blue"'
                fontcolor = ', fontcolor="blue"'

            if len(node.actived_streams) > 0:
                # AN620[label="IteratorV2_IteratorCtrl_StreamSwitch\n(id: 620, stream: 2)"];
                # AS3[label="Stream3"];
                # AN620 -> AS3 [label="active", arrowhead="normal"];
                f.write('AN' + str(node.idx) + '[label="' + node.short_name + '\\n(id: ' + str(node.id) + \
                        ', stream: ' + str(node.stream) + ')"];\n')
                for stream in node.actived_streams:
                    f.write('AS' + str(stream) + '[label="Stream' + str(stream) + '"' + fontcolor + '];\n')
                    f.write('AN' + str(node.idx) + ' -> AS' + str(stream))
                    f.write(' [label="active", arrowhead="normal"' + color + fontcolor + '];\n')
        f.write('}\n')

    '''
    function get object name in dot file
    args self
    args Node node, target node
    return string, object name in dot file
    '''
    def dot_name(self, node):
        if node.stream == -1:
            return 'S_N' + str(node.idx)
        else:
            return 'S' + str(node.stream) + 'N' + str(node.idx)


'''
function tool function, translate num list data to string
args [int] num_list, target list
return string, result string
'''
def num_list_to_str(num_list):
    result = ''
    for num in num_list:
        result = result + ' ' + str(num)
    return result


'''
main entrance
'''
def main(options):
    # 移除文件路径和扩展名
    (file_basename, _) = os.path.splitext(os.path.split(options.file)[1])

    graphs = Parser().parse(options.file)
    if len(graphs) == 0:
        msg = 'parse out no graph, graph file is invalid\n'
        print(msg)
        exit()

    graph = Graph.merge(graphs)
    graph.cfg.show_l2_tag = options.show_l2_tag

    if options.dump_text:
        graph.dump_text(file_basename)

    exec_record = Parser().parse_exec_record_file(options.exec_record_file, options.device_id, graph)

    graph.run_exec_record(exec_record)

    saver = Saver(graph)
    saver.cfg.save_graph = options.save_graph
    saver.cfg.show_all_nodes = options.show_all_nodes
    saver.cfg.light_nodes = options.light_nodes
    saver.cfg.start_node = options.start_node
    saver.cfg.end_node = options.end_node
    saver.cfg.light_subgraphs = not options.disable_light_subgraphs
    saver.cfg.show_l2_tag = options.show_l2_tag
    saver.save(file_basename)

# 需要预先安装graphviz
# Ubuntu: sudo apt-get install graphviz
# EulerOS: sudo yum install graphviz
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('file', type=str, help='ge_onnx or ge_proto files.')
    parser.add_argument('exec_record_file', type=str, help='device exec record file.')
    parser.add_argument('--device_id', type=int, default=0, help='device id which model execute on.')
    parser.add_argument('--light-nodes', type=str, default='', help='specify the nodes to display.')
    parser.add_argument('--start-node', type=str, default='', help='the start display node on the topological order.')
    parser.add_argument('--end-node', type=str, default='', help='the last display node on the topological order.')
    parser.add_argument('--show-all-nodes', action='store_true', help='display all nodes.')
    parser.add_argument('--dump-text', action='store_true', help='dump nodes in text format.')
    parser.add_argument('--save-graph', action='store_true', help='save nodes to xxx.graph.[png|svg].')
    parser.add_argument('--disable-light-subgraphs', action='store_true', \
                        help='do not use different colors to identify subgraphs.')
    parser.add_argument('--show-l2-tag', action='store_true', \
                        help='display is_first_node and is_last_node attributes.')
    options, _ = parser.parse_known_args()
    main(options)

