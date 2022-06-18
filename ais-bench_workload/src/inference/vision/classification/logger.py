import logging


class Logger(object):
    '''
    日志封装类
    使用方法：
        from logger import log

        log.info('hello world!')
    '''

    def __init__(self, log_file_path, level=logging.INFO):
        '''
            log_file_path 日志文件，全路径带日志文件名
            level 日志级别：DEBUG INFO WARNING ERROR CRITICAL
        '''
        self.curlogger = logging.getLogger()
        self.curlogger.setLevel(level)
        # set log output format
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] [%(filename)s: %(lineno)d]  %(message)s', '%Y-%m-%d %H:%M:%S')

        # file log output setting
        file_handler = logging.FileHandler(log_file_path)
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        self.curlogger.addHandler(file_handler)

        # console log output setting
        console = logging.StreamHandler()
        console.setLevel(level)
        console.setFormatter(formatter)
        self.curlogger.addHandler(console)

log = Logger("infer.log", logging.DEBUG).curlogger
