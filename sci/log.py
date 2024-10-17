import os
import re
import logging

from datetime import datetime
from typing import Any

class Log:
    FORMAT_STRING = (
        "\033[1;33m[%(asctime)s "
        "\033[1;31m%(levelname)s "
        "\033[1;32m%(module)s/%(lineno)d-%(processName)s"
        "\033[1;33m] "
        "\033[0m%(message)s"
    )
    ANSI_ESCAPE = r'\033(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])'
    LOG_PATTERN = "%Y%m%d@%H:%M:%S"

    def __init__(self, level: int = logging.INFO) -> None:
        assert isinstance(level, int)
        self.level = level

        self.logger = logging.getLogger()
        self.logger.setLevel(self.level)

        self.__add_stream_handler()
        self.file_handler = None

    def __add_stream_handler(self) -> None:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(self.level)
        stream_handler.setFormatter(logging.Formatter(Log.FORMAT_STRING))
        self.logger.addHandler(stream_handler)

    def __add_file_handler(self, log_path: str, log_name: str) -> None:
        log_file_path = os.path.join(log_path, f"{log_name}.log")
        log_fmt = logging.Formatter(re.sub(Log.ANSI_ESCAPE, "", Log.FORMAT_STRING))

        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(self.level)
        file_handler.setFormatter(log_fmt)
        self.logger.addHandler(file_handler)
        self.file_handler = file_handler

    def __remove_file_handler(self) -> None:
        if self.file_handler is None:
            return

        self.logger.removeHandler(self.file_handler)
        self.file_handler = None

    def switch(self, log_path: str, log_name: str = "") -> None:
        assert isinstance(log_path, str)
        log_path = os.path.expanduser(log_path)
        os.makedirs(log_path, exist_ok=True)

        assert isinstance(log_name, str)
        if log_name == "":
            log_name = datetime.now().strftime(Log.LOG_PATTERN)

        self.__remove_file_handler()
        self.__add_file_handler(log_path, log_name)

    # use log.info() directly instead of log.logger.info()
    def __getattr__(self, attr) -> Any:
        return getattr(self.logger, attr)

