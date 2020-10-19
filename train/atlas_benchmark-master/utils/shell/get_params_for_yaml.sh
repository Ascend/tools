#!/bin/bash

#  解析 yaml 文件中的配置, 并以键值对形式输出
#  args:
#      $1: yaml 文件路径
#      $2: 要获取的节点名
#
#  return:
#      key1=value1
#      key2=value2
#      ...
#
#  可以使用
#  `eval $(./get_params_for_yaml.sh $yamlPath $section)`
#  直接将参数作为变量存入内存


params=$(python3.7 -c "import yaml; print('\n'.join(['%s=\"%s\"' % i for i in yaml.load(open(r'$1'), Loader=yaml.FullLoader).get('$2').items()]))")
if [ x"$params" == x"" ];then
    echo "path: $1 not found key: $2"
    exit 1
fi
echo -e "$params"
