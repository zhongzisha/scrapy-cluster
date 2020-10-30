from builtins import object
from collections import OrderedDict
import logging
import sys
import datetime
import os
import errno
import copy

from pythonjsonlogger import jsonlogger
from cloghandler import ConcurrentRotatingFileHandler


class LogFactory(object):
    """
    Goal is to manage Simple LogObject instances
    Like a Singleton
    """
    _instance = None

    @classmethod
    def get_instance(cls, **kwargs):
        if cls._instance is None:
            cls._instance = LogObject(**kwargs)

        return cls._instance


def is_subdict(a, b):
    """
    Return True if a is a subdict of b
    """
    return all((k in b and b[k] == v) for k, v in a.items())


class LogCallbackMixin:

    def parse_log_level(self, log_level):
        MIN_LOG_LEVEL = self.level_dict['DEBUG']
        MAX_LOG_LEVEL = self.level_dict['CRITICAL']

        chrs = log_level[:2]
        if chrs == '<=':
            log_level = log_level[2:]
            log_level_n = self.level_dict[log_level]
            r = range(MIN_LOG_LEVEL, log_level_n + 1)
        elif chrs.startswith('<'):
            log_level = log_level[1:]
            log_level_n = self.level_dict[log_level]
            r = range(MIN_LOG_LEVEL, log_level_n)
        elif chrs == '>=':
            log_level = log_level[2:]
            log_level_n = self.level_dict[log_level]
            r = range(log_level_n, MAX_LOG_LEVEL + 1)
        elif chrs.startswith('>'):
            log_level = log_level[1:]
            log_level_n = self.level_dict[log_level]
            r = range(log_level_n + 1, MAX_LOG_LEVEL + 1)
        elif chrs.startswith('='):
            log_level = log_level[1:]
            log_level_n = self.level_dict[log_level]
            r = range(log_level_n, log_level_n + 1)
        elif chrs == '*':
            r = range(MIN_LOG_LEVEL, MAX_LOG_LEVEL + 1)
        else:
            log_level_n = self.level_dict[log_level]
            r = range(log_level_n, log_level_n + 1)

        return r

    def register_callback(self, log_level, fn, criteria=None):
        criteria = criteria or {}

        num_to_level_map = {v: k for k, v in self.level_dict.items()}
        log_range = self.parse_log_level(log_level)

        for log_n in log_range:
            level = num_to_level_map[log_n]
            self.callbacks[level].append((fn, criteria))

    def fire_callbacks(self, log_level, log_message=None, log_extra=None):
        log_extra = log_extra or {}

        callbacks = self.callbacks[log_level]
        for cb, criteria in callbacks:
            unmatched_criteria = criteria and not is_subdict(criteria, log_extra)
            if unmatched_criteria:
                continue
            else:
                cb(log_message, log_extra)


def _get_time():
    """
    Returns the system time
    """
    return datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S.%fZ')


class LogObject(LogCallbackMixin):
    """
    Easy wrapper for writing use_json logs to a rotating file log
    """

    def __init__(self, use_json=False, stdout=True, name='scrapy-cluster', log_dir='logs', file='main.log',
                 bytes=25000000, backups=5, level='INFO',
                 format_string='%(asctime)s [%(name)s] %(levelname)s: %(message)s', propagate=False,
                 include_extra=False):
        """
        :param stdout: Flag to write logs to stdout or file
        :param use_json: Flag to write use_json logs with objects or just the messages
        :param name: The logger name
        :param log_dir: The directory to write logs into
        :param file: The file name
        :param bytes: The max file size in bytes
        :param backups: The number of backups to keep of the file
        :param level: The logging level string
        :param format_string: The log format
        :param propagate: Allow the log to propagate to other ancestor loggers
        :param include_extra: When not logging use_json, include the 'extra' param

        """
        # set up logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = propagate
        self.use_json = use_json
        self.log_level = level
        self.format_string = format_string
        self.include_extra = include_extra
        self.callbacks = OrderedDict([
            ("DEBUG", []),
            ("INFO", []),
            ("WARNING", []),
            ("ERROR", []),
            ("CRITICAL", []),
        ])
        self.level_dict = {
            "DEBUG": 0,
            "INFO": 1,
            "WARN": 2,
            "WARNING": 2,
            "ERROR": 3,
            "CRITICAL": 4,
        }

        if stdout:
            # set up to std out
            stream_handler = logging.StreamHandler(sys.stdout)
            stream_handler.setLevel(logging.DEBUG)
            formatter = self._get_formatter(use_json)
            stream_handler.setFormatter(formatter)
            self.logger.addHandler(stream_handler)
            self._check_log_level(level)
            self.debug("Logging to stdout")
        else:
            # set up to file
            try:
                # try to make dir
                os.makedirs(log_dir)
            except OSError as exception:
                if exception.errno != errno.EEXIST:
                    raise

            file_handler = ConcurrentRotatingFileHandler(log_dir + '/' + file,
                                                         maxBytes=bytes,
                                                         backupCount=backups)
            file_handler.setLevel(logging.DEBUG)
            formatter = self._get_formatter(use_json)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)
            self._check_log_level(level)
            self.debug("Logging to file: {file}".format(
                file=log_dir + '/' + file))

    def _check_log_level(self, level):
        """
        Ensures a valid log level

        :param level: the asked for level
        """
        if level not in list(self.level_dict.keys()):
            self.log_level = 'DEBUG'
            self.logger.warning("Unknown log level '{lev}', defaulting to DEBUG"
                                .format(lev=level))

    def _get_formatter(self, use_json):
        """
        Return the proper log formatter

        :param use_json: Boolean value
        """
        if use_json:
            return jsonlogger.JsonFormatter()
        else:
            return logging.Formatter(self.format_string)

    def debug(self, message, extra=None):
        """
        Writes an error message to the log

        :param message: The message to write
        :param extra: The extras object to pass in
        """
        if extra is None:
            extra = {}
        if self.level_dict['DEBUG'] >= self.level_dict[self.log_level]:
            extras = self.add_extras(extra, "DEBUG")
            self._write_message(message, extras)
            self.fire_callbacks('DEBUG', message, extra)

    def info(self, message, extra=None):
        """
        Writes an info message to the log

        :param message: The message to write
        :param extra: The extras object to pass in
        """
        if extra is None:
            extra = {}
        if self.level_dict['INFO'] >= self.level_dict[self.log_level]:
            extras = self.add_extras(extra, "INFO")
            self._write_message(message, extras)
            self.fire_callbacks('INFO', message, extra)

    def warn(self, message, extra=None):
        """
        Writes a warning message to the log

        :param message: The message to write
        :param extra: The extras object to pass in
        """
        if extra is None:
            extra = {}
        self.warning(message, extra)

    def warning(self, message, extra=None):
        """
        Writes a warning message to the log

        :param message: The message to write
        :param extra: The extras object to pass in
        """
        if extra is None:
            extra = {}
        if self.level_dict['WARNING'] >= self.level_dict[self.log_level]:
            extras = self.add_extras(extra, "WARNING")
            self._write_message(message, extras)
            self.fire_callbacks('WARNING', message, extra)

    def error(self, message, extra=None):
        """
        Writes an error message to the log

        :param message: The message to write
        :param extra: The extras object to pass in
        """
        if extra is None:
            extra = {}
        if self.level_dict['ERROR'] >= self.level_dict[self.log_level]:
            extras = self.add_extras(extra, "ERROR")
            self._write_message(message, extras)
            self.fire_callbacks('ERROR', message, extra)

    def critical(self, message, extra=None):
        """
        Writes a critical message to the log

        :param message: The message to write
        :param extra: The extras object to pass in
        """
        if extra is None:
            extra = {}
        if self.level_dict['CRITICAL'] >= self.level_dict[self.log_level]:
            extras = self.add_extras(extra, "CRITICAL")
            self._write_message(message, extras)
            self.fire_callbacks('CRITICAL', message, extra)

    def _write_message(self, message, extra):
        """
        Writes the log output
        :param message: The message to write
        :param extra: The potential object to write
        """
        if not self.use_json:
            self._write_standard(message, extra)
        else:
            self._write_json(message, extra)

    def _write_standard(self, message, extra):
        """
        Writes a standard log statement

        :param message: The message to write
        :param extra: The object to pull defaults from
        """
        level = extra['level']
        if self.include_extra:
            del extra['timestamp']
            del extra['level']
            del extra['logger']
            if len(extra) > 0:
                message += " " + str(extra)

        if level == 'INFO':
            self.logger.info(message)
        elif level == 'DEBUG':
            self.logger.debug(message)
        elif level == 'WARNING':
            self.logger.warning(message)
        elif level == 'ERROR':
            self.logger.error(message)
        elif level == 'CRITICAL':
            self.logger.critical(message)
        else:
            self.logger.debug(message)

    def _write_json(self, message, extra):
        """
        The JSON logger doesn't obey log levels

        :param message: The message to write
        :param extra: The object to write
        """
        self.logger.info(message, extra=extra)

    @property
    def name(self):
        """
        Returns the logger name
        """
        return self.logger.name

    def add_extras(self, dict_obj, level):
        """
        Adds the log level to the dict object
        """
        my_copy = copy.deepcopy(dict_obj)
        if 'level' not in my_copy:
            my_copy['level'] = level
        if 'timestamp' not in my_copy:
            my_copy['timestamp'] = _get_time()
        if 'logger' not in my_copy:
            my_copy['logger'] = self.name
        return my_copy
