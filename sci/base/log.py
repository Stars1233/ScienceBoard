import logging
import os
import re
import json
import random
import string

from datetime import datetime
from PIL import Image

from typing import Optional, List, Dict, Any
from typing import Callable, Self, TYPE_CHECKING

if TYPE_CHECKING:
    from .task import Task
    from .agent import CodeLike

class Log:
    # use self.PROPERTY instead of Log.PROPERTY to
    # make it easier to change outside of the class, e.g.
    #   log = Log()
    #   log.LOG_PATTERN = "%Y%m%d%H%M%S"
    #   log.switch("~/Downloads")
    #   log.info("Test")
    ANSI_ESCAPE = r'\033(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])'
    LOG_PATTERN = (
        "\033[1;91m[%(asctime)s "
        "\033[1;91m%(levelname)s "
        "\033[1;94mID=%(domain)s "
        "\033[1;92m%(module)s::%(funcName)s@%(filename)s:%(lineno)d"
        "\033[1;91m] "
        "\033[0m%(message)s"
    )

    @property
    def FILE_LOG_PATTERN(self) -> str:
        return re.sub(self.ANSI_ESCAPE, "", self.LOG_PATTERN)

    LEGACY_MARKER = "LAGACY@"
    SUM_LOG_PREFIX = "SUM@"
    DEFAULT_DOMAIN = "GLOBAL"
    TIMESTAMP_PATTERN = "%y%m%d%H%M%S"

    @property
    def __timestamp(self) -> str:
        return datetime.now().strftime(self.TIMESTAMP_PATTERN)

    IMAGE_FILENAME   = "step_{index}@{timestamp}.png"
    TEXT_FILENAME    = "step_{index}@{timestamp}.txt"

    TRAJ_FILENAME    = "traj.jsonl"
    RESULT_FILENAME  = "result.out"
    RECORD_FILENAME  = "record.mp4"
    REQUEST_FILENAME = "request.json"

    @property
    def traj_file_path(self):
        assert self.file_handler is not None
        return os.path.join(self.save_path, self.TRAJ_FILENAME)

    @property
    def result_file_path(self):
        assert self.file_handler is not None
        return os.path.join(self.save_path, self.RESULT_FILENAME)

    @property
    def record_file_path(self):
        assert self.file_handler is not None
        return os.path.join(self.save_path, self.RECORD_FILENAME)

    @property
    def request_file_path(self):
        assert self.file_handler is not None
        return os.path.join(self.save_path, self.REQUEST_FILENAME)

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

        self.extra = {"domain": self.DEFAULT_DOMAIN}
        self.adapter = logging.LoggerAdapter(self.logger, self.extra)
        self.logger = self.adapter.logger

        assert isinstance(disabled, bool)
        self.logger.disabled = disabled

        if not self.logger.disabled:
            self.__add_stream_handler()

        self.file_handler = None
        self._registered = []
        self._independent = []

    # this cannot be called in __del__()
    # because open (__builtin__) cannot be found then
    # so callback() should be manually called by its owner
    def callback(self) -> None:
        for file_handler in self._independent:
            self.__remove_file_handler(file_handler)

        for handler in self._registered:
            handler(self)
        self._registered.clear()

    @property
    def save_path(self) -> Optional[str]:
        return os.path.split(self.file_handler.baseFilename)[0] \
            if self.file_handler is not None else None

    @property
    def save_name(self) -> str:
        assert self.file_handler is not None
        return os.path.split(self.file_handler.baseFilename)[1]

    def __add_stream_handler(self) -> None:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(self.level)
        stream_handler.setFormatter(logging.Formatter(self.LOG_PATTERN))
        self.logger.addHandler(stream_handler)
        self.stream_handler = stream_handler

    def __add_file_handler(
        self,
        log_path: str,
        log_name: str,
        dependent: bool = True
    ) -> None:
        log_file_path = os.path.join(log_path, f"{log_name}.log")
        log_formatter = logging.Formatter(self.FILE_LOG_PATTERN)

        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(self.level)
        file_handler.setFormatter(log_formatter)

        self.logger.addHandler(file_handler)
        if dependent:
            self.file_handler = file_handler
        else:
            self._independent.append(file_handler)
        self.register(Log.replace_ansi, file_handler.baseFilename)

    def __remove_file_handler(
        self,
        file_handler: Optional[logging.FileHandler] = None
    ) -> None:
        if self.file_handler is None:
            return

        if file_handler is None:
            file_handler = self.file_handler

        if file_handler == self.file_handler:
            self.file_handler = None

        self.logger.removeHandler(file_handler)

    # dependent=True: to remove previous file_handler if exists
    def trigger(
        self,
        log_path: str,
        log_name: str = "",
        prefix: str = "",
        dependent: bool = True
    ) -> None:
        assert isinstance(log_path, str)
        log_path = os.path.expanduser(log_path)
        os.makedirs(log_path, exist_ok=True)

        assert isinstance(log_name, str)
        if log_name == "":
            log_name = self.__timestamp

        assert isinstance(prefix, str)

        if dependent:
            self.__remove_file_handler()
        self.__add_file_handler(
            log_path,
            prefix + log_name,
            dependent=dependent
        )

    def __clear(self, ignore: bool) -> bool:
        if os.path.exists(self.result_file_path) and ignore:
            return

        for filename in os.listdir(self.save_path):
            file_path = os.path.join(self.save_path, filename)
            # the org of tasks dir is never assumed
            # so there might be dirs in extreme cases
            if os.path.isfile(file_path) and not filename.endswith(".log"):
                os.remove(file_path)
            # automatically add LEGACY_MARKER to old log file
            elif os.path.isfile(file_path) \
                and not filename.startswith(self.LEGACY_MARKER) \
                and filename != self.save_name:
                new_file_path = os.path.join(
                    self.save_path,
                    self.LEGACY_MARKER + filename
                )
                os.rename(file_path, new_file_path)

    # tricks of passing args to `with` block
    # ref: https://stackoverflow.com/a/10252925
    def __call__(
        self,
        base_path: str = None,
        ident: str = None,
        ignore: bool = True,
        in_exit: bool = False
    ) -> Self:
        self.extra["domain"] = self.DEFAULT_DOMAIN if ident is None else ident

        # called in __exit__()
        # in_exit should not be called manually
        if in_exit:
            self.__remove_file_handler()
        # called before __enter__()
        else:
            assert base_path is not None
            log_path = os.path.join(base_path, ident)
            os.makedirs(log_path, exist_ok=True)
            self.trigger(log_path)
            self.__clear(ignore)
        return self

    def __enter__(self) -> bool:
        return os.path.exists(self.result_file_path)

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self(in_exit=True)

    @staticmethod
    def replace_ansi(file_path: str) -> Callable[["Log"], None]:
        def handler(self: Log) -> None:
            log_content = open(file_path, mode="r", encoding="utf-8").read()
            with open(file_path, mode="w", encoding="utf-8") as writable:
                writable.write(re.sub(self.ANSI_ESCAPE, "", log_content))
        return handler

    @staticmethod
    def delete(file_path: str) -> Callable[["Log"], None]:
        def handler(self: Log) -> None:
            try:
                os.remove(file_path)
            except FileNotFoundError: ...
        return handler

    def register(
        self,
        handler: Callable[[str], Callable[["Log"], None]],
        file_path: Optional[str] = None
    ) -> None:
        if file_path is None:
            assert self.file_handler is not None
            file_path = self.file_handler.baseFilename
        self._registered.append(handler(file_path))

    def save(
        self,
        step_index: int,
        obs: Dict[str, Any],
        codes: List["CodeLike"],
        request: Dict[str, Any]
    ) -> None:
        assert self.save_path is not None, "Call switch() first"

        timestamp = self.__timestamp
        traj_obj = {
            "step_index": step_index,
            "timestamp": self.__timestamp,
            "actions": [code_like.code for code_like in codes]
        }

        text_file_name = self.TEXT_FILENAME.format(
            index=step_index,
            timestamp=timestamp
        )
        text_file_path = os.path.join(self.save_path, text_file_name)

        image_filename = self.IMAGE_FILENAME.format(
            index=step_index,
            timestamp=timestamp
        )
        image_file_path = os.path.join(self.save_path, image_filename)

        # save a11y_tree to new file
        filtered_text = [
            item for _, item in obs.items()
            if isinstance(item, str)
        ]
        if len(filtered_text) == 1:
            traj_obj["screenshot"] = text_file_name
            with open(text_file_path, mode="r", encoding="utf-8") as writable:
                writable.write(filtered_text[0])

        # save screenshot (or SoM screenshot) to new file
        filtered_image = [
            item for _, item in obs.items()
            if isinstance(item, Image.Image)
        ]
        if len(filtered_image) == 1:
            traj_obj["a11y_tree"] = image_filename
            filtered_image[0].save(image_file_path)

        # save trajetories by appending previous records
        with open(self.traj_file_path, mode="a", encoding="utf-8") as appendable:
            appendable.write(json.dumps(traj_obj, ensure_ascii=False) + "\n")

        # save requests by overwriting previous record
        with open(self.request_file_path, mode="w", encoding="utf-8") as writable:
            json.dump(request, writable, ensure_ascii=False, indent=2)

    def result_handler(method: Callable) -> Callable:
        def wrapper(self: "Task", stop_type: staticmethod) -> bool:
            return_value = method(self, stop_type)
            with open(
                self.vlog.result_file_path,
                mode="w",
                encoding="utf-8"
            ) as writable:
                writable.write(str(int(return_value)))
            return return_value
        return wrapper

    def record_handler(method: Callable) -> Callable:
        def wrapper(self: "Task") -> bool:
            self.manager.record_start()
            return_value = method(self)
            self.manager.record_stop(self.vlog.record_file_path)
            return return_value
        return wrapper

    # use log.info() directly instead of self.adapter.info()
    # WARNING:
    #   __getattr__ will not be called if property can be found directly
    #   in these functions, self.logger (:= self.adapter.logger) is used, while
    #   in __getattr__, self.adapter is used (to fill domain formatter)
    def __getattr__(self, attr: str) -> Any:
        return getattr(self.adapter, attr)

    # to be a hint for user input
    # we suggested setting level to CRITICAL
    # although there is no error occurred
    def input(
        self,
        msg: str,
        level: int = logging.CRITICAL,
        end: str ="\n"
    ) -> str:
        stored_end = self.stream_handler.terminator
        self.stream_handler.terminator = end
        self.adapter.log(level=level, msg=msg)
        self.stream_handler.terminator = stored_end
        return input()


class VirtualLog:
    def __init__(self) -> None:
        self.log = None

    def set(self, log: Log):
        assert isinstance(log, Log)
        self.log = log

    # use vlog.info() directly instead of vlog.log.adapter.info()
    def __getattr__(self, attr: str) -> Any:
        log = Log(disabled=True) if self.log is None else self.log
        return getattr(log, attr)
