import logging
import os
from logging.handlers import TimedRotatingFileHandler


class ExactLogLevelFilter(logging.Filter):
    def __init__(self, level):
        super().__init__()
        self.__level = level

    def filter(self, log_record):
        return log_record.levelno == self.__level


class Log(object):
    def __init__(self, name='Crawler', path='logs/', when='D', backcount=7):
        """
        :param name: logger name
        :param path: logs path
        :param when: how many time the backup would be saved
        :param backcount: the number of backup
        """

        self.__logger = logging.getLogger(name)
        self.__logger.setLevel(logging.DEBUG)

        self._handlers = dict()
        self._backcount = backcount
        self._when = when

        self.log_path = {
            'DEBUG': os.path.join(path, 'debug/debug.log'),
            'INFO': os.path.join(path, 'info/info.log'),
            'WARN': os.path.join(path, 'warn/warn.log'),
            'ERROR': os.path.join(path, 'error/error.log')
        }
        self._create_handlers()

    def _create_handlers(self):
        log_levels = self.log_path.keys()

        for level in log_levels:
            path = os.path.abspath(self.log_path[level])

            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))

            self._handlers[level] = TimedRotatingFileHandler(path, when=self._when, backupCount=self._backcount)
            self._handlers[level].setFormatter(logging.Formatter(u'%(asctime)s\t%(pathname)s:%(lineno)s\t%(levelname)s\t%(message)s'))
            self._handlers[level].addFilter(ExactLogLevelFilter(getattr(logging, level)))

            self.__logger.addHandler(self._handlers[level])

    def debug(self, message):
        self.__logger.debug(message)

    def info(self, message):
        self.__logger.info(message)

    def warn(self, message):
        self.__logger.warn(message)

    def error(self, message):
        self.__logger.error(message)

LOG = Log()
