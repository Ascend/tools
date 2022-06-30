import math

import loadgen

QueryArrivalMode_map = {
    "continuous": loadgen.QueryArrivalMode.CONTINUOUS_MODE,
    "periodic": loadgen.QueryArrivalMode.PERIODIC_MODE,
    "poison_distribute": loadgen.QueryArrivalMode.POISON_DISTRIBUTE_MODE,
    "offline": loadgen.QueryArrivalMode.OFFLINE_MODE,
    "mixed": loadgen.QueryArrivalMode.MIXED_MODE
}

def run_loadgen(datasets, backend, postproc, args):
    if args.maxloadsamples_count == None:
        maxloadsamples_count = datasets.get_samples_count
    else:
        maxloadsamples_count = args.maxloadsamples_count

    if maxloadsamples_count < datasets.get_samples_count:
        samplesPerQuery = maxloadsamples_count
    else:
        samplesPerQuery = datasets.get_samples_count

    # 创建QSL设备
    params = loadgen.QslParams()
    params.totalSamplesCount = datasets.get_samples_count
    params.maxLoadSamplesCount = maxloadsamples_count
    params.loadSamplesCb = datasets.load_query_sample
    params.unloadSamplesCb = datasets.unload_query_sample
    qsl = loadgen.CreateQSL(params)

    # fill param and creat sut
    # 创建SUT设备
    params = loadgen.SUTParams()
    params.preProcessCb = datasets.pre_proc_func
    params.predictProcessCb = backend.predict_proc_func
    params.postProcessCb = postproc.post_proc_func
    params.flushQueries = datasets.flush_queries
    sut = loadgen.CreateSUT(params)

    # fill setting 填写配置
    settings = loadgen.TestSettings()

    # 离线模式设置
    settings.arrivalMode = QueryArrivalMode_map[args.query_arrival_mode]
    if args.query_arrival_mode == "offline":
        settings.samplesPerQuery = samplesPerQuery
        settings.minQueryCount = math.ceil(datasets.get_samples_count/settings.samplesPerQuery)
        settings.targetQPS = samplesPerQuery
        settings.latencyConstraintNs = 100*3600*1000000000
    elif args.query_arrival_mode == "continuous":
        settings.samplesPerQuery = samplesPerQuery
        settings.minQueryCount = math.ceil(datasets.get_samples_count/settings.samplesPerQuery)
        settings.targetQPS = samplesPerQuery
    elif args.query_arrival_mode == "periodic":
        settings.samplesPerQuery = samplesPerQuery
        settings.minQueryCount = math.ceil(datasets.get_samples_count/settings.samplesPerQuery)
        settings.targetQPS = samplesPerQuery
    else:
        raise RuntimeError('arrival mode:{} not support'.format(args.query_arrival_mode))

    # start test 启动测试
    loadgen.StartTest(sut, qsl, settings)

    backend.sumary()

    # 销毁句柄
    loadgen.DestroyQSL(qsl)
    loadgen.DestroySUT(sut)
