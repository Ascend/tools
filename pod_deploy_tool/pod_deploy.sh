#!/bin/bash
# Copyright 2022 Huawei Technologies Co., Ltd
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#########################################################################

function remove_single_quote() {
    local tmp=$*
    local var=${tmp#?}
    var=${var%?}
    echo "${var}"
}

function use_help() {
    echo "--work_dir atlas edge work dir, eg:/usr/local/AtlasEdge"
    echo "--operate  pod operate type, create ore delete"
    echo "--pod_file absolute path of pod yaml file"
}

function main() {
    local para=( "$@" )
    local args
    args=$(getopt -o h -a -l help,"work_dir:,operate:,pod_file:" -n "pod_deploy.sh" -- "$@")
    if [[ $? != 0 ]];then
        echo "parse para failed, try '--help' for more information"
        return 1
    fi

    set -- ${args}
    while true ; do
        case "$1" in
        --work_dir | -work_dir)
          atlas_edge_work=$(remove_single_quote "$2")
          shift 2
          ;;
        -h | --help)
          use_help
          return 1
          ;;
        --)
          shift
          break
          ;;
        *)
          shift 2
          ;;
        esac
    done

    if [[ ! -e ${atlas_edge_work}/edge_work_dir/edge_om/env_profile.sh ]]; then
        echo "work_dir ${atlas_edge_work} invalid, try '--help' for more information"
        return 1
    fi

    source "${atlas_edge_work}"/edge_work_dir/edge_om/env_profile.sh
    python3 pod_deploy.py "${para[@]}"
}

main "$@"
exit $?