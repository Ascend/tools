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
    GRAPH_FILE = 0

    # collection
    EXCEPTION_PATTERN = r"<exception_print>TIME:(\d+-\d+-\d+-\d+:\d+:\d+\.\d+\.\d+)[ \S]+?" \
                        r"device_id=(\d+)[ \S]+?stream_id=(\d+)[ \S]+?task_id=" \
                        r"(\d+).+?AICORE_INFO_START: core_id=(\d+).+?AIC_ERROR=" \
                        r"(\S+).+?PC_START=(\S+)(.+?)CURRENT_PC=(\S+)"

    AIC_ERROR_INFO_DICT = {
        175: "vec_err_parity_err, VEC 中发生奇偶校验错误",
        174: "vec_valu_ill_issue, VALU 指令传输顺序违反 ISA 约束",
        173: "vec_pb_read_no_resp, SU 从 VEC 接收 PB 读取请求后长时间不响应",
        172: "vec_pb_ecc_mberr, SU 返回给 VEC 的 PB 数据包含 ECC 错误",
        171: "vec_biu_resp_err, BIU 返回给 VEC 的数据错误",
        170: "vec_ic_ecc_err, 从 VEC ICACHE 中获取的指令发生 ECC 错误",
        169: "vec_ill_vga_vpd_order, VAG 和 VPD 命令的顺序违反 IAS 约束",
        168: "vec_ill_instr_padding, VAG 和 VPD 的 PADDING 指令不是 VNOP",
        167: "vec_st_num_exceed_limit, st 指令数量超过 ISA 中指定的最大值",
        166: "vec_ld_num_exceed_limit, ld 指令数量超过 ISA 中指定的最大值",
        165: "vec_ex_num_mismatch, ex 指令所在的代码段包含非 ex 指令",
        164: "vec_st_num_mismatch, st 指令所在的代码段包含非 st 指令",
        163: "vec_ld_num_mismatch, ld 指令所在的代码段包含非 ld 指令",
        162: "vec_ill_vloop_sreg, 第 4 层的 VLOOP 循环次数全部为 0",
        161: "vec_ill_vloop_op, VLOOP 指令中的操作码错误",
        160: "vec_vci_idata_out_range, VCI 指令的输入数据超出范围",
        159: "vec_valu_neg_sqrt, VALU squart 操作的输入数据是负数",
        158: "vec_valu_neg_ln, VALU lN 操作的输入数据是负数",
        157: "vec_div_by_zero, VEC 的除零错误",
        156: "vec_idata_inf_nan, 指令操作的输入数据是 INF/NAN",
        155: "vec_ub_ecc_mberr, 访问 UB 时发生多位 ECC 错误",
        154: "vec_ub_addr_wrap_around, UB 的访问地址超出范围",
        153: "vec_instr_ill_sqzn, sqzn 值无效",
        152: "vec_instr_ill_mask, 掩码值无效",
        151: "vec_instr_misalign, 指令访问 UB 地址未对齐",
        150: "vec_instr_ill_cfg, VEC 指令配置非法",
        149: "vec_instrs_undef, 指令在 ISA 中未定义",
        148: "vec_instr_timeout, 指令运行超时",
        147: "vec_data_excpt_vec, VECTOR 写入/读取时报告数据异常",
        146: "vec_data_excpt_su, SU 写入/读取时报告数据异常",
        145: "vec_data_excpt_mte, MTE 写入/读取时报告数据异常",
        144: "mte_err_l0c_rdwr_cflt, FIXP 读取 L0C 时发生读写操作冲突",
        143: "fixp_l0c_ecc, FIXP 指令错误：读取 L0C 时的 ECC 验证失败",
        142: "cube_err_pbuf_wrap_around, CUBE FIXP_BUFFER 发生循环错误",
        141: "fixp_err_out_write_overflow, FIXP 写入溢出错误",
        140: "ccu_cross_core_set_ovfl_err, 跨核心通信的标志计数器值超过最大值 15",
        139: "ccu_lsu_atomic_err, 标量 LSU 执行原子操作失败",
        138: "mte_aipp_ecc_err, MTE AIPP 中发生多位 ECC 错误",
        137: "mte_stb_ecc_err, MTE STB 中发生多位 ECC 错误",
        136: "biu_unsplit_err, BIU 上发生异常，例如 tag_id 错误或 FIFO 溢出",
        135: "ccu_ub_overflow_err, AIC 和 AIV 共享 UB 时发生 LS/ST 访问覆盖",
        134: "ccu_ub_wr_cflt, Lite Only 错误，CCU 向 UB 写入数据时发生 UB 读/写冲突",
        133: "ccu_ub_rd_cflt, Lite Only 错误，CCU 读取 UB 时发生 UB 读/写冲突",
        132: "mte_ktable_rd_addr_overflow, MTE 为空时发生读地址冲突并报告异常",
        131: "mte_ktable_wr_addr_overflow, MTE 满时发生写地址冲突并报告异常",
        130: "mte_ub_wr_cflt, Lite Only 错误，MTE 写入 UB 时发生 UB 读/写冲突",
        129: "mte_ub_rd_cflt, Lite Only 错误，MTE 读取 UB 时发生 UB 读/写冲突并报告异常",
        128: "mte_timeout, Lite Only 错误，MTE 指令或数据超时",
        127: "ccu_safety_crc_err, MTE CRC 错误",
        126: "cube_illegal_instr, CUBE 指令配置非法",
        125: "mte_ub_rd_ovflw, MTE 读取 UB 地址溢出",
        124: "mte_ub_wr_ovflw, MTE 写入 UB 地址溢出",
        123: "ccu_pb_ecc_err, 参数缓冲区出现 2 位 ECC 错误",
        122: "ccu_lsu_err, 缓冲区启用时，堆栈访问指令缓存缺失",
        121: "ccu_mpu_err, MPU 地址访问无效",
        120: "ccu_seq_err, SEQ 命令序列不正确",
        119: "mte_err_waipp, WAIPP 指令配置非法",
        118: "mte_err_hebce, HEBCE 指令配置非法",
        117: "mte_err_hebcd, HEBCD 指令配置非法",
        116: "mte_err_instr_illegal_cfg, MTE 指令配置非法",
        115: "cube_err_hset_cnt_ovf, CUBE HSET 计数器上溢错误",
        114: "cube_err_hset_cnt_unf, CUBE HSET 计数器下溢错误",
        113: "mte_err_cache_ecc, MTE 内部 MVF 缓存故障",
        112: "ccu_err_parity_err, 安全功能期间 SU 内部缓冲区出现奇偶校验错误",
        111: "mte_err_waitset, HWATI/HSET 配置不正确",
        110: "mte_err_fifo_parity, 从 MTE 内部 FIFO 读取的数据不正确",
        109: "sc_reg_parity_err, 安全检查期间 nManager 寄存器出现奇偶校验错误",
        108: "fixp_err_fbuf_read_ovflw, FBUF 的读取地址超出范围",
        107: "fixp_err_fbuf_write_ovflw, FBUF 的写入地址超出范围",
        106: "fixp_err_write_ub_ovflw, UB 的写入地址超出范围",
        105: "fixp_err_write_l1_ovflw, L1 的写入地址超出范围",
        104: "fixp_err_read_ub_ovflw, UB 的读取地址超出范围",
        103: "fixp_err_read_l1_ovflw, L1 的读取地址超出范围",
        102: "fixp_err_read_l0c_ovflw, L0C 的读取地址超出范围",
        101: "fixp_err_illegal_cfg, FIXP 配置非法",
        100: "fixp_err_instr_addr_misal, 读取 L0C、读取 L1 和写入 FIXP 缓冲区地址不对齐",
        99: "cnt_sw_bus_err, 在慢速上下文切换期间，SC 通过 AXI 总线传输数据，AXI 返回错误",
        98: "ccu_neg_sqrt_fp, FP SQRT 计算单元的输入为负数",
        97: "ccu_div0_fp, FP32 DIV0 错误",
        96: "ccu_dc_tag_ecc, 数据缓存标签 RAM 中出现 2 位 ECC 错误",
        95: "ccu_dc_data_ecc, 数据缓存数据 RAM 中出现 2 位 ECC 错误",
        94: "ccu_veciq_ecc, VEC 问题队列中出现 2 位 ECC 错误",
        93: "mte_err_read_3d_overflow, MTE load3d指令的读取溢出",
        92: "mte_err_illegal_smallk_cfg, MTE load3d指令的small K配置不正确",
        91: "mte_err_illegal_k_m_start_pos, K_M_START_POS的值非法",
        90: "mte_err_illegal_k_m_ext_step, K_M_EXT_STEP的值非法",
        89: "mte_err_illegal_chn_size, CHN_SIZE的值非法",
        88: "mte_err_illegal_h_size, WINOA fmap H的值非法",
        87: "mte_err_illegal_w_size, WINOA fmap W的值非法",
        86: "mte_err_illegal_h_cov_pad_ctl, WINOA H padding的值非法",
        85: "mte_err_illegal_v_cov_pad_ctl, WINOA V padding的值非法",
        84: "mte_err_wino_l0b_read_overflow, WINOB读取的L1地址溢出，发生了循环",
        83: "mte_err_wino_l0b_write_overflow, WINOB向L0B地址写入时发生溢出",
        82: "mte_err_dw_fmap_h_illegal, DEPTHWISE FMAP上配置的H值小于3",
        81: "mte_err_dw_pad_conf_err, DEPTHWISE PADDING配置错误",
        80: "mte_err_addr_misalign, 指令地址不对齐（ADDR_MISALIGN）",
        79: "ccu_bus_err, D-cache读写UB时，总线返回的响应值为非零值",
        78: "ccu_addr_err, CCU指令地址检查错误",
        77: "vec_instr_undef, 当前VEC版本不支持的指令",
        76: "vec_instr_illegal_cfg, VEC支持非法配置的指令",
        75: "vec_instr_addr_misalign, VEC指令访问的UB地址未对齐",
        74: "mte_atm_addr_misalg, MTE原子加地址未对齐（AIC、AIV1、AIV2）",
        73: "mte_illegal_schn_cfg, small_channel使能标志有效，但不满足small_channel的条件",
        72: "ccu_inf_nan, CCU执行的浮点指令的输入为nan/inf",
        71: "vec_col2img_illegal_k_size, col2img的值非法",
        70: "vec_col2img_illegal_fetch_pos, col2img的值非法",
        69: "vec_col2img_illegal_1st_win_pos, col2img的值非法",
        68: "vec_col2img_illegal_stride, col2img的值非法",
        67: "vec_col2img_illegal_fm_size, col2img的值非法",
        66: "vec_col2img_rd_dfm_addr_ovfflow, col2img的值非法",
        65: "vec_col2img_rd_fm_addr_ovflow, col2img的值非法",
        64: "ccu_sbuf_ecc, 在CCU的scalar buffer中报了ECC错误",
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
    
    IFU_KEY = "IFU_ERR_INFO"
    CCU_KEY = "CCU_ERR_INFO"
    BIU_KEY = "BIU_ERR_INFO"
    CUBE_KEY = "CUBE_ERR_INFO"
    MTE_KEY = "MTE_ERR_INFO"
    VEC_KEY = "VEC_ERR_INFO"

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
