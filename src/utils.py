import functools
import logging

from typing import Dict, Type
import logging

from logstash_formatter import LogstashFormatterV1

class CustomLogger:
    def __init__(self, cls: Type, config: Dict[str, str]) -> None:
        self._config = config
        self._logger: logging.Logger = self._create_logger(cls)
        self._setup()

    @staticmethod
    @functools.cache
    def _create_logger(cls: Type) -> logging.Logger:
        return logging.getLogger(f'{cls.__module__}.{cls.__name__}')

    def _setup(self) -> None:
        self._logger.setLevel(self.get_logging_level())
        handler = self.get_handler()
        handler.setFormatter(self.get_formatter())
        self._logger.addHandler(handler)

    def get_logging_level(self) -> int:
        logging_level = self._config.get('level', 'info').upper()
        if hasattr(logging, logging_level):
            return getattr(logging, logging_level)
        else:
            return logging.INFO

    def get_formatter(self) -> logging.Formatter:
        """Get logging formatter based on the configuration"""
        formatter = self._config.get('formatter', '').lower()
        if formatter == 'logstash':
            return LogstashFormatterV1()
        else:
            return logging.Formatter('[%(asctime)s: %(levelname)s/%(processName)s] %(filename)s %(lineno)d %(message)s')

    def get_handler(self) -> logging.Handler:
        handler_type = self._config.get('handler', '').lower()
        if handler_type == 'syslog':
            return logging.handlers.SysLogHandler(address='/dev/log')
        elif handler_type == 'file':
            return logging.FileHandler(self._config['log_path'])
        else:
            return logging.StreamHandler()

    def __call__(self) -> logging.Logger:
        return self._logger
