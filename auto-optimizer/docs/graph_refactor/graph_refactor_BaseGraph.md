# BaseGraph

## 概念定义

- BaseGraph 由节点（算子节点、常量节点、输入输出节点）列表组成，根据算子节点的输入输出存储和更新连边关系，形成有向无环图。
- BaseGraph 可以理解为从 onnx 模型解析得到的图 IR，改图操作均在图 IR 层面进行。

## 相关操作

BaseGraph 类提供了基本的接口用于增删改查节点：

| API 详细说明                                 | **Operations**              | **API**                                                      |
| -------------------------------------------- | --------------------------- | ------------------------------------------------------------ |
| [查询节点](./graph_refactor_API.md#查询节点) | 根据节点名称查询单个节点        | g[name]                                                      |
|                                              | 根据节点类型查询节点        | g.get_nodes(op_type)                                         |
|                                              | 根据节点名称和类型查询单个节点        | g.get_node(name, node_type)                                         |
|                                              | 查询前驱节点                | g.get_prev_node(input_name)                                  |
|                                              | 查询后继节点                | g.get_next_nodes(output_name)                                |
|                                              | 查询节点输入/输出的维度信息 | g.get_value_info(io_name)                                    |
| [修改节点](./graph_refactor_API.md#修改节点) | 修改单个节点                | g[name] = new_node                                           |
|                                              | 修改节点信息                | 详见[BaseNode说明](./graph_refactor_BaseNode.md)             |
| [添加节点](./graph_refactor_API.md#添加节点) | 添加整网输入节点            | g.add_input(name, dtype, shape)                              |
|                                              | 添加整网输出节点            | g.add_output(name, dtype, shape)                             |
|                                              | 添加算子节点                | g.add_node(name, op_type, attrs)                             |
|                                              | 添加常量节点                | g.add_initializer(name, value)                               |
| [插入节点](./graph_refactor_API.md#插入节点) | 插入单输入单输出节点        | g.insert_node(refer_name, insert_node,refer_index, mode)     |
|                                              | 插入多输入多输出节点        | g.connect_node(insert_node, prev_nodes_info, next_nodes_info) |
| [删除节点](./graph_refactor_API.md#删除节点) | 删除单个节点                | g.remove(name)                                               |
|                                             | 删除多余节点                | g.remove_unused_nodes()                                               |

除此之外，BaseGraph 类提供的其它功能如下所示：

| API 详细说明                                 | **Operations**     | **API**                                                 |
| -------------------------------------------- | ------------------ | ------------------------------------------------------- |
| [属性](./graph_refactor_API.md#属性)         | 获取整网输入节点   | g.inputs                                                |
|                                              | 获取整网输出节点   | g.outputs                                               |
|                                              | 获取所有算子节点   | g.nodes                                                 |
|                                              | 获取所有常量节点   | g.initializers                                          |
|                                              | 获取所有形状信息   | g.value_infos                                           |
|                                              | 获取opset_imports  | g.opset_imports                                         |
|                                              | 修改opset_imports  | g.opset_imports = int                                   |
| [基础功能](./graph_refactor_API.md#基础功能) | 解析模型文件       | OnnxGraph.parse(path_or_bytes)                          |
|                                              | 将图保存成模型文件 | g.save(path)                                            |
|                                              | 图转为GraphProto   | g.proto()                                               |
|                                              | 图转为ModelProto   | g.model()                                               |
|                                              | 更新前后节点关系   | g.update_map()                                          |
|                                              | 算子节点拓扑排序   | g.toposort()                                            |
| [实用功能](./graph_refactor_API.md#实用功能) | 模型截断           | g.extract(save_path, input_name_list, output_name_list) |
|                                              | 形状推断           | g.infershape()                                          |
|                                              | 模型简化           | g.simplify(**kwargs)                                    |
