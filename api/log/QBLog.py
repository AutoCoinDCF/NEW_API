#!/user/bin/env python
# -*-coding:utf-8 -*-
import logging

'''
%(levelname)s 文本形式的日志级别
%(asctime)s 字符串形式的当前时间。默认格式是 “2003-07-08 16:49:45,896”。逗号后面的是毫秒
%(name)s Logger的名字
%(funcName)s 调用日志输出函数的函数名
%(lineno)d 调用日志输出函数的语句所在的代码行
%(message)s 用户输出的消息
'''


class QBLog:
    __levels = {
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'DEBUG': logging.DEBUG,
    }

    def __init__(self, config, name=None):
        # 文件的命名
        self.logger = logging.getLogger(name)
        self.logger.setLevel(
            self.__levels.get(config.get('LOG_LEVEL'), logging.INFO)
        )
        # 日志输出格式
        self.formatter = logging.Formatter(
            '[%(asctime)s - %(filename)s - %(lineno)d] - %(levelname)s:-----> %(message)s')

    def __console(self, level, message):
        # 创建一个StreamHandler,用于输出到控制台
        ch = logging.StreamHandler()
        ch.setLevel(logging.DEBUG)
        ch.setFormatter(self.formatter)
        self.logger.addHandler(ch)
        if level == 'info':
            self.logger.info(message)
        elif level == 'debug':
            self.logger.debug(message)
        elif level == 'warning':
            self.logger.warning(message)
        elif level == 'error':
            self.logger.error(message)
        # 这两行代码是为了避免日志输出重复问题
        self.logger.removeHandler(ch)

    def debug(self, message):
        self.__console('debug', message)

    def info(self, message):
        self.__console('info', message)

    def warning(self, message):
        self.__console('warning', message)

    def error(self, message):
        self.__console('error', message)


if __name__ == "__main__":
    log = QBLog()
    log.info("---测试开始----")
    log.warning("----测试结束----")
