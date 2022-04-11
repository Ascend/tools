#!/usr/bin/env python
# coding=utf-8
"""
Function:
This file mainly involves the constant variables.
Copyright Information:
Huawei Technologies Co., Ltd. All Rights Reserved © 2020
"""

import os
import stat


class Constant:
    """
    The class for constant.
    """
    # error code for user:success
    MS_AICERR_NONE_ERROR = 0
    # error code for user: error
    MS_AICERR_INVALID_PARAM_ERROR = 1
    MS_AICERR_INVALID_PATH_ERROR = 2
    MS_AICERR_CONNECT_ERROR = 3
    MS_AICERR_INVALID_DUMP_DATA_ERROR = 4
    MS_AICERR_OPEN_FILE_ERROR = 5
    MS_AICERR_EXECUTE_COMMAND_ERROR = 6
    MS_AICERR_INVALID_CONFIG_DATA_ERROR = 7
    MS_AICERR_INVALID_SLOG_DATA_ERROR = 8
    MS_AICERR_FIND_DATA_ERROR = 9

    WRITE_FLAGS = os.O_WRONLY | os.O_CREAT
    WRITE_MODES = stat.S_IWUSR | stat.S_IRUSR

    DIRECTORY_MASK = 0o700

    BUILD_PROTO_FILE_PATTERN = r"^ge_proto_(\d+)_Build\.txt$"
    MAX_READ_FILE_BYTES = 1024 * 1024  # 1M
    MAX_TAR_SIZE = 1 * 1024 * 1024 * 1024   # 1G

    SCRIPT = "script"

    TYPE_COMPILE = 'compile'
    TYPE_DUMP = 'dump'
    TYPE_BBOX = 'bbox'

    DIR_ASCEND = 'ascend'
    DIR_LOG = 'log'
    DIR_SLOG = 'slog'
    DIR_BBOX = 'hisi_logs'
    DIR_PLOG = 'plog'

    AIC_ERROR_TUPLE_LEN = 9
    # dump_data_parser
    UINT64_SIZE = 8
    TIME_LENGTH = 1000
    UINT64_FMT = 'Q'

    STRUCT_FORMAT_KEY = 'struct_format'
    DTYPE = 'dtype'

    SIZE_OF_DTYPE = {"DT_FLOAT": 4, "DT_FLOAT16": 2, "DT_INT8": 1, "DT_INT16": 2,
                     "DT_UINT16": 2, "DT_UINT8": 1, "DT_INT32": 4, "DT_INT64": 8,
                     "DT_UINT32": 4, "DT_UINT64": 8, "DT_BOOL": 1, "DT_DOUBLE": 8,
                     "DT_STRING, -1}, {DT_DUAL_SUB_INT8": 1, "DT_DUAL_SUB_UINT8": 1, "DT_COMPLEX64": 8,
                     "DT_COMPLEX128, 16}, {DT_QINT8": 1, "DT_QINT16": 2, "DT_QINT32": 4,
                     "DT_QUINT8": 1, "DT_QUINT16": 2, "DT_RESOURCE": -1, "DT_STRING_REF": -1,
                     "DT_DUAL": 5}
    #aicore_error_parser
    OBJ_DUMP_FILE = "cce-objdump"
    ADDR_OVERFLOW = 0
    ALLOC_ADDR = 1
    ACTUAL_ADDR = 2
    GRAPH_FILE = 3

    # collection
    EXCEPTION_PATTERN = r"<exception_print>TIME:(\d+-\d+-\d+-\d+:\d+:\d+\.\d+\.\d+)[ \S]+?" \
                        r"device_id=(\d+)[ \S]+?stream_id=(\d+)[ \S]+?task_id=" \
                        r"(\d+).+?AICORE_INFO_START: core_id=(\d+).+?AIC_ERROR=" \
                        r"(\S+).+?PC_START=(\S+)(.+?)CURRENT_PC=(\S+)"

    AIC_ERROR_INFO_DICT = {
        63: """biu_dfx_err，BIU模块返回了一个综合型错误，把所有的错误类型或在一起""",
        62: """vec_ub_wrap_around，vector指令自动计算UB地址时发生越界，X或者VA寄存器已经越界的情况不报此错误""",
        61: """vec_ub_self_rdwr_cflt，vector指令同时读写了UB的同一个地址，仅针对lite平台""",
        60: """vec_ub_ecc，ecc error，硬件问题""",
        59: """vec_same_blk_addr，vector指令在同一个repeat写了相同的block，代码不会写出这样的指令，一般为硬件问题；
        VEC_ERR_INFO中的vec_err_rcnt记录了出错的repeat""",
        58: """vec_neg_sqrt，VSQRT指令被开方数为负数，VEC_ERR_INFO中的vec_err_rcnt记录了出错的repeat""",
        57: """vec_neg_ln，VLN指令的操作数为负数，VEC_ERR_INFO中的vec_err_rcnt记录了出错的repeat""",
        56: """vec_l0c_rdwr_cflt，L0C读写同地址冲突，比如MMAD指令写L0C地址与MOV指令读L0C地址相同，
        CUBE_ERR_INFO中的cube_err_addr记录了冲突的地址""",
        55: """vec_l0c_ecc，ecc error，硬件问题""",
        54: """vec_inf_nan，vector指令的操作数为Inf或者NaN，VEC_ERR_INFO中的vec_err_rcnt记录了出错的repeat""",
        53: """vec_illegal_mask，vector指令MASK域段为全0，VEC_ERR_INFO中的vec_err_rcnt记录了出错的repeat""",
        52: """vec_div0，VREC指令发生除0错误，VEC_ERR_INFO中的vec_err_rcnt记录了出错的repeat""",
        51: """vec_data_excp_vec，vector指令访问的UB地址，超过了DATA_EXP寄存器设置的UB访问地址范围""",
        50: """vec_data_excp_mte，mte指令访问的UB地址，超过了DATA_EXP寄存器设置的UB访问地址范围""",
        49: """vec_data_excp_ccu，scalar指令访问的UB地址，超过了DATA_EXP寄存器设置的UB访问地址范围""",
        48: """mte_write_overflow，LOAD 2D写地址越界""",
        47: """mte_write_3d_overflow，LOAD 3D写地址越界""",
        46: """mte_unzip，unzip指令异常，MTE_ERR_INFO中的mte_err_type记录了异常类型：
    000 uzp_write_over_turn_err
    001 uzp_blk_num_zero_err
    010 uzp_index_noenough_err
    011 uzp_index_err
    100 uzp_decompress_err""",
        45: """mte_ub_ecc，ecc error，硬件问题""",
        44: """mte_tlu_ecc，ecc error，硬件问题""",
        43: """mte_rob_ecc，ecc error，硬件问题""",
        42: """mte_read_overflow，LOAD 2D读地址越界""",
        41: """mte_padding_cfg，LOAD 3D指令padding配置错误，和padding有关的一些限制如下：
    1. Feature_map_size_w(after padding)>Filter_size_w(after dilation)
    2. Feature_map_size_h(after padding)>=Filter_size_h(after dilation)
    3. 1st filter window position <= Feature map size (with padding) – Filter size (after dilation)
    4. Stride size <= Feature map size (with padding) – Filter size (after dilation).This formula fit 
    for the entire feature map in convolution. In terms of a single 3D Load instruction, the feature 
    map may be partial. Then in w dimension, the formula is tenable; In H dimension, 
    it should be ignored.""",
        40: """mte_l1_ecc，ecc error，硬件问题""",
        39: """mte_l0b_rdwr_cflt，L0B读写同地址冲突，比如L0AD 3D指令写L0B地址与MMAD指令读L0B地址相同，
        CUBE_ERR_INFO中的cube_err_addr记录了冲突的地址""",
        38: """mte_l0a_rdwr_cflt，L0A读写同地址冲突，比如L0AD 3D指令写L0A地址与MMAD指令读L0A地址相同，
        MTE_ERR_INFO中的mte_err_addr记录了冲突的地址""",
        37: """mte_illegal_stride，L0AD 3D指令stride配置错误，有关的一些限制如下：
    1. Stride size, W dimension ∈[1, 63](Bit width[5:0]), H dimension ∈[1, 63](Bit width[5:0])
    2. Stride size <= Feature map size (with padding) – Filter size (after dilation).This formula fit 
    for the entire feature map in convolution. In terms of a single 3D Load instruction, 
    the feature map may be partial. Then in w dimension, the formula is tenable; In H dimension, 
    it should be ignored.""",
        36: """mte_illegal_l1_3d_size，L0AD 3D指令L1_3D_SIZE配置错误，有关的一些限制如下：
    FeatureMapW * FeatureMapH * (CIndex +Cincr+1) <= L1_3D_size""",
        35: """mte_illegal_fm_size，L0AD 3D指令feature map size配置错误，有关的一些限制如下：
    1. Feature_map_size_w(after padding)>Filter_size_w(after dilation)
    Feature_map_size_h(after padding)>=Filter_size_h(after dilation)
    2. 1st filter window position <= Feature map size (with padding) – Filter size (after dilation).
    3. Stride size <= Feature map size (with padding) – Filter size (after dilation).This formula fit 
    for the entire feature map in convolution. In terms of a single 3D Load instruction, 
    the feature map may be partial. Then in w dimension, the formula is tenable; In H dimension, 
    it should be ignored.
    4. Due to L1 Buffer size is 1MB, Feature map size (without padding) and C dimension index should 
    meet: FeatureMapW * FeatureMapH * (CIndex +1) <= 32768 When repeat mode=0, 
    the C index increment should be consider(Cincr denote the increment of C0 index during repeat):
    FeatureMapW * FeatureMapH * (CIndex +Cincr+1) <= 32768
    When set L1 3D size is valid
    FeatureMapW * FeatureMapH * (CIndex +Cincr+1) <= L1_3D_size""",
        34: """mte_comp，FMC指令异常，当前index未处理完又下发新的index table，
        MTE_ERR_INFO中的mte_err_type记录了异常类型：
    000 fmc_read_over_turn_err 
    001 fmc_blk_num_zero_err""",
        33: """mte_gdma_write_overflow，DMA MOV指令写越界""",
        32: """mte_gdma_read_overflow，DMA MOV指令读越界""",
        31: """mte_gdma_illegal_burst_num，DMA MOV指令burst_num不合法，不能为0""",
        30: """mte_gdma_illegal_burst_len，DMA MOV指令burst_len不合法，不能为0""",
        29: """mte_fpos_larger_fsize，L0AD 3D指令fetch position in filter 大于 filter size""",
        28: """mte_fmapwh_larger_l1size，L0AD 3D指令w*h*c大于L1 size""",
        27: """mte_fmap_less_kernel，L0AD 3D指令feature map size小于kernel size""",
        26: """mte_f1wpos_larger_fsize，L0AD 3D指令1st filter window position大于Feature map size –
        Filter size""",
        25: """mte_decomp，FMD指令异常，load index entry的数量和它后面最近的一个load decompressed data
        要解压的数据块数量不一致，MTE_ERR_INFO中的mte_err_type记录了异常类型：
    000 fmd_write_over_turn_err
    001 fmd_blk_num_zero_err
    010 fmd_blk_num_noequal_err
    011 fmd_header_err
    100 fmd_decompress_err""",
        24: """mte_cidx_overflow，L0AD 3D指令c0 index L1 overflow""",
        23: """mte_biu_rdwr_resp，通过BIU读写out数据错误，MTE_ERR_INFO中的mte_err_type记录了异常类型，
        mte_err_addr记录了发生错误的地址（是触发问题的另一面的地址，比如out -> L1读错误，记的是L1地址，
        又如ub -> out写错误，记的是ub地址）""",
        22: """mte_bas_raddr_obound，L0AD 3D指令base read addr（Xn）越界""",
        21: """mte_aipp_illegal_param，AIPP指令aipp_spr寄存器配置有误，
        MTE_ERR_INFO中的mte_err_type记录了异常类型：
    3'b000: aipp_mte_ex_round : 表示访问外部存储绕回
    3'b001: aipp_mte_l1_round : 表示访问L1 buffer绕回
    3'b010: aipp_mte_inerr : 表示配置AIPP SPR相关的fp16为INF或者NAN""",
        20: """ifu_bus_err，BIU返回bus error给IFU，意味着从out取指令错误，
        IFU_ERR_INFO中的ifu_err_type记录了异常类型，ifu_err_addr记录了错误的地址""",
        19: """cube_l0c_wrap_around，cube指令自动计算L0C地址时发生越界，X或者VA寄存器已经越界的情况不报此错误""",
        18: """cube_l0c_self_rdwr_cflt，前后两条指令的L0C地址相同，可能同时出现对相同的L0C地址同时读写的场景，
        CUBE_ERR_INFO中的cube_err_addr记录了冲突的地址""",
        17: """cube_l0c_rdwr_cflt，L0C读写同地址冲突，比如MMAD指令写L0C地址与MOV指令读L0C地址相同，
        CUBE_ERR_INFO中的cube_err_addr记录了冲突的地址""",
        16: """cube_l0c_ecc，ecc error，硬件问题""",
        15: """cube_l0b_wrap_around，cube指令自动计算L0B地址时发生越界，X或者VA寄存器已经越界的情况不报此错误""",
        14: """cube_l0b_rdwr_cflt，L0B读写同地址冲突，比如L0AD 3D指令写L0B地址与MMAD指令读L0B地址相同，
        CUBE_ERR_INFO中的cube_err_addr记录了冲突的地址""",
        13: """cube_l0b_ecc，ecc error，硬件问题""",
        12: """cube_l0a_wrap_around，cube指令自动计算L0A地址时发生越界，X或者VA寄存器已经越界的情况不报此错误""",
        11: """cube_l0a_rdwr_cflt，L0A读写同地址冲突，比如L0AD 3D指令写L0A地址与MMAD指令读L0A地址相同，
        MTE_ERR_INFO中的mte_err_addr记录了冲突的地址""",
        10: """cube_l0a_ecc，ecc error，硬件问题""",
        9: """cube_invld_input，cube指令的输入（L0A/L0B/L0C）数据含有NaN或者Inf，包含L0C累加场景""",
        8: """ccu_ub_ecc，ecc error，硬件问题""",
        7: """ccu_neg_sqrt，sqrt指令出现被开方数为负数""",
        6: """ccu_loop_err，有程序jump，从其他地方跳到loop body中""",
        5: """ccu_loop_cnt_err，loop循环次数设置为0""",
        4: """ccu_illegal_instr，非法执行：1.指令的binary错误  2.指令地址非对齐""",
        3: """ccu_div0，scalar出现除0错误""",
        2: """ccu_call_depth_ovrflw，函数调用深度超过设置值""",
        1: """biu_l2_write_oob，L2访问写越界，BIU_ERR_INFO中的biu_err_addr记录了越界的地址""",
        0: """biu_l2_read_oob，L2访问读越界，BIU_ERR_INFO中的biu_err_addr记录了越界的地址""",
    }

    SOC_ERR_INFO_DICT = {"000": "read poison, 读到脏数据",
                         "001": "read oob, 表示L2在作为buffer模式时，读地址超过了配置的L2虚拟地址的size",
                         "010": "read bus error, 读请求时数据异常，例如安全访问请求访问了非安全的地址，"
                                "非安全访问的请求访问了安全地址，访问请求收不到response、atomic运算异常(1980)",
                         "011": "read decode error, 读请求访问的目的地址不在各个模块的地址空间内，也即越界",
                         "101": "write oob, 表示L2在作为buffer模式时，写地址超过了配置的L2虚拟地址的size",
                         "110": "write bus error, 写请求时数据异常，例如安全访问请求访问了非安全的地址，"
                                "非安全访问的请求访问了安全地址，访问请求收不到response、atomic运算异常(1980)",
                         "111": "write decode error, 写请求访问的目的地址不在各个模块的地址空间内，也即越界"}

    FMC_ERR_INFO_DICT = {"000": "fmc_read_over_turn_err",
                         "001": "fmc_blk_num_zero_err"}

    FMD_ERR_INFO_DICT = {"000": "fmd_write_over_turn_err",
                         "001": "fmd_blk_num_zero_err",
                         "010": "fmd_blk_num_noequal_err",
                         "011": "fmd_header_err",
                         "100": "fmd_decompress_err"}

    UNZIP_ERR_INFO_DICT = {"000": "uzp_write_over_turn_err",
                           "001": "uzp_blk_num_zero_err",
                           "010": "uzp_index_noenough_err",
                           "011": "uzp_index_err",
                           "100": "uzp_decompress_err"}

    AIPP_ERR_INFO_DICT = {"000": "aipp_mte_ex_round : 表示访问外部存储绕回",
                          "001": "aipp_mte_l1_round : 表示访问L1 buffer绕回",
                          "010": "aipp_mte_inerr : 表示配置AIPP SPR相关的fp16为INF或者NAN"}

    @property
    def max_top_n(self: any) -> int:
        """
        max top n
        """
        return 100

    @property
    def min_top_n(self: any) -> int:
        """
        mix top n
        """
        return 1
