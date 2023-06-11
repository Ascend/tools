#!/bin/bash

check_python_package_is_install() {
    local PYTHON_COMMAND=$1
    ${PYTHON_COMMAND} -c "import $2" >>/dev/null 2>&1
    ret=$?
    if [ $ret != 0 ]; then
        echo "python package:$1 not install"
        return 1
    fi
    return 0
}
