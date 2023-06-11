#!/bin/bash
CUR_DIR=$(dirname $(readlink -f $0))
TOP_DIR=${CUR_DIR}/..
TEST_DIR=${TOP_DIR}/"test"
SRC_DIR=${TOP_DIR}/"src"/"python"

clean() {
    cd ${TEST_DIR}

    if [ -e ${TEST_DIR}/"report" ]; then
      rm -r ${TEST_DIR}/"report"
      echo "remove last ut_report successfully."
    fi

    if [ -e ${SRC_DIR}/"build" ]; then
      cd ${SRC_DIR}
      rm -r build
      rm -r ptdbg_ascend.egg-info
      echo "remove last build cache."
    fi

    if [ -e ${SRC_DIR}/"ptdbg_ascend"/"common"/"version.py" ]; then
      rm ${SRC_DIR}/"ptdbg_ascend"/"common"/"version.py"
      echo "remove last generated 'version.py'."
    fi
}

run_ut() {
    export PYTHONPATH=${SRC_DIR}:${PYTHONPATH} && python3 run_ut.py
}

main() {
    clean
    if [ "$1"x == "clean"x ]; then
      return 0
    fi

    cd ${SRC_DIR} && python3 setup.py build
    cd ${TEST_DIR} && run_ut
}

main $@
