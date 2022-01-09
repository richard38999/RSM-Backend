# coding:utf-8
import logging
import time
import os

class Log():
    def __init__(self, Log_folder):
        # cur_path = os.path.dirname(os.path.realpath(__file__))
        currentlyPath = os.getcwd()
        self.log_path = os.path.join(currentlyPath, 'logs\\' + Log_folder)
        # 如果不存在这个logs文件夹，就自动创建一个
        if not os.path.exists(self.log_path):
            os.mkdir(self.log_path)
        #文件的命名
        self.logName = '%s.log'%time.strftime('%Y%m%d')
        self.log_full_name = os.path.join(self.log_path,self.logName)
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        #日志输出格式
        self.formatter = logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s')
    def __console(self,level,message):
        #创建一个FileHandler，用于写到本地
        fh = logging.FileHandler(self.log_full_name,'a',encoding='utf-8')#这个是python3的
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(self.formatter)
        self.logger.addHandler(fh)
        #创建一个StreamHandler,用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(self.formatter)
        self.logger.addHandler(ch)
        #区分日志级别
        if level =='info':
            self.logger.info(message)
        elif level =='debug':
            self.logger.debug(message)
        elif level =='warning':
            self.logger.warning(message)
        elif level =='error':
            self.logger.error(message)
        elif level =='start':
            message = '*********************************************** {0} Start ***********************************************\r'.format(message)
            self.logger.info(message)
        elif level =='end':
            message = '*********************************************** {0} End ***********************************************\r'.format(message)
            self.logger.info(message)
        #避免日志输出重复问题
        self.logger.removeHandler(ch)
        self.logger.removeHandler(fh)
        #关闭打开的文件
        ch.close()
        fh.close()
    def debug(self,message):
        self.__console('debug',message)
    def info(self,message):
        self.__console('info',message)
    def warning(self,message):
        self.__console('warning',message)
    def error(self,message):
        self.__console('error',message)
    def start(self,message):
        self.__console('start', message)
    def end(self,message):
        self.__console('end', message)