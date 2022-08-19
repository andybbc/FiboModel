# -*- coding: utf-8 -*-
import os
import sys
import logging


""" 单实例Logger 模块"""
class Singleton(object):
    __cls = {}

    def __init__(self, cls):
        self.__key = cls

    def __call__(self, *args, **kw):
        if self.__key not in self.cls:
            self[self.__key] = self.__key(*args, **kw)

        return self[self.__key]

    def __setitem__(self, key, value):
        self.cls[key] = value

    def __getitem__(self, item):
        return self.cls[item]

    def __repr__(self):
        return str(self.__key)

    @property
    def cls(self):
        return self.__cls

    @cls.setter
    def cls(self, cls):
        self.__cls = cls


@Singleton
class Logger(object):
    def __init__(self,
                 level='INFO',
                 name=os.path.split(os.path.splitext(sys.argv[0])[0])[-1],
                 format_str='%(asctime)s [%(pathname)s:%(lineno)d][%(funcName)s][%(name)s][%(levelname)s] %(message)s',
                 log_path=os.path.join(os.path.abspath(os.getcwd()), 'log'),
                 file_handler='file_time',  # file or file_time
                 command_line=False):

        if not level:
            level = self._exec_type()

        self.__logger = logging.getLogger(name)

        self.setLevel(getattr(logging, level.upper() if hasattr(logging, level.upper()) else logging.INFO))

        formater = logging.Formatter(format_str)

        handlers = []
        handlers.append(self.select_handler(file_handler, log_path))
        if command_line:
            handlers.append(logging.StreamHandler())

        for handler in handlers:
            handler.setFormatter(formater)
            self.addHandler(handler)

    def __getattr__(self, item):
        return getattr(self.logger, item)

    def select_handler(self, name, log_path):
        if name == 'file':
            return logging.FileHandler(log_path, mode='w')
        elif name == 'file_time':
            from logging.handlers import TimedRotatingFileHandler
            file_time_handler = TimedRotatingFileHandler(log_path, 'H', 1, 24 * 15, 'utf8')
            file_time_handler.suffix = '%Y%m%d%H'
            return file_time_handler

    @property
    def logger(self):
        return self.__logger

    @logger.setter
    def logger(self, func):
        self.__logger = func

    def _exec_type(self):
        return "DEBUG" if os.environ.get("IPYTHONENABLE") else "INFO"


if __name__ == "__main__":
    print(Logger)
