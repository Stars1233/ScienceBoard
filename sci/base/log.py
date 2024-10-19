import logging
import os
import re
import random
import string

from datetime import datetime
from typing import Any

class Log:
    # use self.PROPERTY instead of Log.PROPERTY
    # to make it easier to change outside of the class
    # e.g.
    #   log = Log()
    #   log.LOG_PATTERN = "%Y%m%d%H%M%S"
    #   log.switch("~/Downloads")
    #   log.info("TEST")
    FORMAT_STRING = (
        "\033[1;33m[%(asctime)s "
        "\033[1;31m%(levelname)s "
        "\033[1;32m%(module)s/%(lineno)d-%(processName)s"
        "\033[1;33m] "
        "\033[0m%(message)s"
    )
    ANSI_ESCAPE = r'\033(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])'
    LOG_PATTERN = "%Y%m%d@%H%M%S"

    @property
    def FILE_FORMAT_STRING(self) -> str:
        return re.sub(self.ANSI_ESCAPE, "", self.FORMAT_STRING)

    def __init__(
        self,
        level: int = logging.INFO,
        disabled: bool = False
    ) -> None:
        assert isinstance(level, int)
        self.level = level

        # if two logs' name clashes
        # you should buy yourself some lotteries
        log_name = "".join(random.choice(
            string.ascii_uppercase + string.digits
        ) for _ in range(64))
        self.logger = logging.getLogger(log_name)
        self.logger.setLevel(self.level)

        assert isinstance(disabled, bool)
        self.logger.disabled = disabled

        self.__add_stream_handler()
        self.file_handler = None

    @property
    def __timestamp(self):
        return datetime.now().strftime(self.LOG_PATTERN)

    def __add_stream_handler(self) -> None:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(self.level)
        stream_handler.setFormatter(logging.Formatter(self.FORMAT_STRING))
        self.logger.addHandler(stream_handler)

    def __add_file_handler(
        self,
        log_path: str,
        log_name: str,
        record_new: bool = True
    ) -> None:
        log_file_path = os.path.join(log_path, f"{log_name}.log")
        log_fmt = logging.Formatter(self.FILE_FORMAT_STRING)

        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(self.level)
        file_handler.setFormatter(log_fmt)
        self.logger.addHandler(file_handler)
        if record_new:
            self.file_handler = file_handler

    def __remove_file_handler(self) -> None:
        if self.file_handler is None:
            return

        self.logger.removeHandler(self.file_handler)
        self.file_handler = None

    def __file(
        self,
        log_path: str,
        log_name: str = "",
        prefix: str = "",
        delete_old: bool = True
    ) -> None:
        assert isinstance(log_path, str)
        log_path = os.path.expanduser(log_path)
        os.makedirs(log_path, exist_ok=True)

        assert isinstance(log_name, str)
        if log_name == "":
            log_name = self.__timestamp

        assert isinstance(prefix, str)

        if delete_old:
            self.__remove_file_handler()
        self.__add_file_handler(
            log_path,
            prefix + log_name,
            record_new=delete_old
        )

    def switch(
        self,
        log_path: str,
        log_name: str = "",
        prefix: str = ""
    ) -> None:
        self.__file(log_path, log_name, prefix, delete_old=True)

    def new(
        self,
        log_path: str,
        log_name: str = "",
        prefix: str = ""
    ) -> None:
        self.__file(log_path, log_name, prefix, delete_old=False)

    # use self.info() directly instead of self.logger.info()
    def __getattr__(self, attr: str) -> Any:
        return getattr(self.logger, attr)


class VirtualLog:
    def __init__(self) -> None:
        self.log = None

    def set(self, log: Log):
        assert isinstance(log, Log)
        self.log = log

    def __getattr__(self, attr: str) -> Any:
        log = Log(disabled=True) if self.log is None else self.log
        return getattr(log, attr)
