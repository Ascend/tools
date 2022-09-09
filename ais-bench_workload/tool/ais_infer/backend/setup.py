import os
import sys

from pybind11 import get_cmake_dir
# Available at setup time due to pyproject.toml
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

__version__ = "0.0.1"

# The main interface is through Pybind11Extension.
# * You can add cxx_std=11/14/17, and then build_ext can be removed.
# * You can set include_pybind11=false to add the include directory yourself,
#   say from a submodule.
#
# Note:
#   Sort input source files if you glob sources to ensure bit-for-bit
#   reproducible builds (https://github.com/pybind/python_example/pull/53)

cann_base_path = None

def get_cann_path():
    global cann_base_path
    set_env_path=os.getenv("CANN_PATH", "")
    atlas_nnae_path = "/usr/local/Ascend/nnae/latest/"
    atlas_toolkit_path = "/usr/local/Ascend/ascend-toolkit/latest/"
    hisi_fwk_path = "/usr/local/Ascend/"
    check_file_path = "acllib/lib64/stub/libascendcl.so"
    if os.path.exists(set_env_path+check_file_path):
        cann_base_path = set_env_path
    elif os.path.exists(atlas_nnae_path+check_file_path):
        cann_base_path = atlas_nnae_path
    elif os.path.exists(atlas_toolkit_path+check_file_path):
        cann_base_path = atlas_toolkit_path
    elif os.path.exists(hisi_fwk_path+check_file_path):
        cann_base_path = hisi_fwk_path

    if cann_base_path == None:
        raise RuntimeError('error find no cann path')
    print("find cann path:", cann_base_path)

get_cann_path()

ext_modules = [
    Pybind11Extension(
        'aclruntime',
        # Sort input source files to ensure bit-for-bit reproducible builds
        # (https://github.com/pybind/dnmetis_backend/pull/53)
        #sorted(['src/main.cpp','src/model_process.cpp','src/sample_process.cpp','src/utils.cpp']),
        sources=[
            'base/module/DeviceManager/DeviceManager.cpp',
            'base/module/ErrorCode/ErrorCode.cpp',
            'base/module/Log/Log.cpp',
            'base/module/MemoryHelper/MemoryHelper.cpp',
            'base/module/Tensor/TensorBase/TensorBase.cpp',
            'base/module/Tensor/TensorBuffer/TensorBuffer.cpp',
            'base/module/Tensor/TensorContext/TensorContext.cpp',
            'base/module/ModelInfer/model_process.cpp',
            'base/module/ModelInfer/utils.cpp',
            'base/module/ModelInfer/SessionOptions.cpp',
            'base/module/ModelInfer/ModelInferenceProcessor.cpp',
            'python/src/PyInterface/PyInterface.cpp',
            'python/src/PyTensor/PyTensor.cpp',
            'python/src/PyInferenceSession/PyInferenceSession.cpp',
            

        ],
        include_dirs=[
            'python/include/',
            'base/include/',
            'base/include/Base/ModelInfer/',
            cann_base_path + '/acllib/include',
        ],
        #library_dirs=['output/lib/',],
        library_dirs=[ cann_base_path + '/acllib/lib64/stub/',],
        
        extra_compile_args = ['--std=c++11', '-g3'],

        libraries=['ascendcl', 'acl_dvpp', 'acl_cblas'],
        language='c++',
        define_macros = [('ENABLE_DVPP_INTERFACE', 1), ('COMPILE_PYTHON_MODULE', 1)],
    ),
]

setup(
    name = "aclruntime",
    version=__version__,
    author="lcm",
    author_email="aclruntime@gmail.com",
    url="https://xxxxx",
    description="A test project using pybind11 and aclruntime",
    long_description="",
    ext_modules = ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
    python_requires=">=3.6",
)