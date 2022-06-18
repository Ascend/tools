# encoding:utf-8
import logging
import time
 
class Log(object):
    """
        console log
        usages:
            from logger import log
            class ClassName():    # class that uses log
                log.info("log message") 
                log.debug(">>>>>Log Message: %s, %s" % ("Hello", "I'm debug log")) 
                log.info("lcm debug idx:{} a:{}".format(idx, a))        
        example:   
            2018-01-17 22:45:05,447 [DEBUG] test_mainrun.py test_run_mail line:31 please input name
            2018-01-17 22:45:05,447 [INFO]  operate success
    """
    global log
    log = None
    @staticmethod
    def init_logger(level = logging.INFO, logger_name = None):
        
        logger = logging.getLogger(logger_name)
        logger.setLevel(level)
        log_time = time.strftime("%Y_%m_%d_")
        # console handler
        ch = logging.StreamHandler()
        ch.setLevel(level)
        formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
        if (level == logging.DEBUG):
            formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(funcName)s line:%(lineno)d %(message)s')            
                    
        ch.setFormatter(formatter)
       
        logger.addHandler(ch)
 
        # release handler
        ch.close()
        return logger
    
log = Log().init_logger()
