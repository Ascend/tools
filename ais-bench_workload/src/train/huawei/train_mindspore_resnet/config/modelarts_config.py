from easydict import EasyDict as ed

access_config = ed({
    # 登录需要的ak sk信息
    'access_key': '',
    'secret_access_key': '',
    # 连接OBS的服务地址。可包含协议类型、域名、端口号。（出于安全性考虑，建议使用https协议）
    # 如果是计算中心，需要联系运维同事获取
    'server': '',
    # project_id/region_name:
    # 项目ID/区域ID，获取方式参考链接
    # https://support.huaweicloud.com/api-iam/iam_17_0002.html
    # 如果是计算中心,请咨询相关维护同事
    'region_name': '',
    'project_id': '',

    # 如下配置针对计算中心等专有云 通用云不需要设置 设置为空 请咨询相关维护同事
    # 设置该信息后 需要设置相关的域名解析地址
    'iam_endpoint': '',
    'obs_endpoint': '',
    'modelarts_endpoint' : '',
})

session_config = ed({
    'hyperparameters': [
        {'label': 'config_path', 'value': 'resnet50_imagenet2012_Boost_config.yaml'},
        {'label': 'enable_modelarts', 'value': 'True'},
        {'label': 'run_distribute', 'value': 'True'},
        {'label': 'epoch_size', 'value': '5'},
        {'label': 'device_num', 'value': '8'},
        {'label': 'save_checkpoint', 'value': 'True'},
        {'label': 'save_checkpoint_epochs', 'value': '5'},
    ],
    # 输入数据集目录
    'inputs': '/zgwtest/lcm_test/dataset/imagenet_small/',
    # obs代码路径 程序会自动拷贝到该路径
    'code_dir': '/zgwtest/lcm_test/resnet/',
    # 启动文件 必须要在code_dir路径下
    'boot_file': '/zgwtest/lcm_test/resnet/train.py',

    # 如下为运行相关参数
    # job名称  如果云环境Modelarts服务训练作业job队列中没有，则会新建一个job；若和已有job同名，则会在该job中，新建测试实例.
    'job_name': "aisbench-debug",

    # 使用容器类型与镜像版本
    'framework_type': 'Ascend-Powered-Engine',
    'framework_version': 'MindSpore-1.2.0-c77-python3.7-euleros2.8-aarch64',

    # 专属资源池id 不是为None类型
    'pool_id' : 'pool09811b1c',
    # 训练类型 如下为8卡 如果是专属资源池id设置，那么该类型需要设置为None
    'train_instance_type': None,    #'modelarts.kat1.8xlarge',
    # 训练结点数
    'train_instance_count': 2,

    # 云存储路径 默认为空
    'nas_type' : None,
    'nas_share_addr' : None,
    'nas_mount_path' : None,

    # 输出信息基准路径 整体路径为 train_url = out_base_url/version_name
    "out_base_url": "/zgwtest/lcm_test/result",
    # job 描述前缀
    "job_description_prefix": 'lcm-debug desc',
})
