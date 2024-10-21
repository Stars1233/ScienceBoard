import logging
import os
import re
import json
import random
import string

from datetime import datetime
from PIL import Image

from typing import Optional, List, Dict, Any
from typing import Callable, TYPE_CHECKING

if TYPE_CHECKING:
    from .task import Task
    from .agent import CodeLike

class Log:
    # use self.PROPERTY instead of Log.PROPERTY
    # to make it easier to change outside of the class
    # e.g.
    #   log = Log()
    #   log.LOG_PATTERN = "%Y%m%d%H%M%S"
    #   log.switch("~/Downloads")
    #   log.info("TEST")
    ANSI_ESCAPE = r'\033(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])'
    LOG_PATTERN = (
        "\033[1;33m[%(asctime)s "
        "\033[1;31m%(levelname)s "
        "\033[1;32m%(module)s/%(lineno)d-%(processName)s"
        "\033[1;33m] "
        "\033[0m%(message)s"
    )
    TIMESTAMP_PATTERN = "%y%m%d%H%M%S"

    TRAJ_FILENAME   = "traj.jsonl"
    IMAGE_FILENAME  = "step_{index}@{timestamp}.png"
    TEXT_FILENAME   = "step_{index}@{timestamp}.txt"

    RESULT_FILENAME = ".out"
    RECORD_FILENAME = "record.mp4"

    @property
    def FILE_LOG_PATTERN(self) -> str:
        return re.sub(self.ANSI_ESCAPE, "", self.LOG_PATTERN)

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

        if not self.logger.disabled:
            self.__add_stream_handler()
        self.file_handler = None

        # self.save_path is sync-ed with switch()
        self.save_path: Optional[str] = None

    @property
    def __timestamp(self):
        return datetime.now().strftime(self.TIMESTAMP_PATTERN)

    def __add_stream_handler(self) -> None:
        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(self.level)
        stream_handler.setFormatter(logging.Formatter(self.LOG_PATTERN))
        self.logger.addHandler(stream_handler)

    def __add_file_handler(
        self,
        log_path: str,
        log_name: str,
        record_new: bool = True
    ) -> None:
        log_file_path = os.path.join(log_path, f"{log_name}.log")
        log_formatter = logging.Formatter(self.FILE_LOG_PATTERN)

        file_handler = logging.FileHandler(log_file_path)
        file_handler.setLevel(self.level)
        file_handler.setFormatter(log_formatter)
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
        self.save_path = log_path
        self.__file(log_path, log_name, prefix, delete_old=True)

    def new(
        self,
        log_path: str,
        log_name: str = "",
        prefix: str = ""
    ) -> None:
        self.__file(log_path, log_name, prefix, delete_old=False)

    def save(
        self,
        step_index: int,
        obs: Dict[str, Any],
        codes: List["CodeLike"]
    ) -> None:
        assert self.save_path is not None, "Call switch() first"

        timestamp = self.__timestamp
        traj_file_path = os.path.join(self.save_path, self.TRAJ_FILENAME)
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

        # save a11y_tree
        filtered_text = [
            item for _, item in obs.items()
            if isinstance(item, str)
        ]
        if len(filtered_text) == 1:
            traj_obj["screenshot"] = text_file_name
            with open(text_file_path, mode="r", encoding="utf-8") as writable:
                writable.write(filtered_text[0])

        # save screenshot (or SoM screenshot)
        filtered_image = [
            item for _, item in obs.items()
            if isinstance(item, Image.Image)
        ]
        if len(filtered_image) == 1:
            traj_obj["a11y_tree"] = image_filename
            filtered_image[0].save(image_file_path)

        # save trajetories
        with open(traj_file_path, mode="a", encoding="utf-8") as appendable:
            appendable.write(json.dumps(traj_obj) + "\n")

    def result_handler(method: Callable) -> Callable:
        def wrapper(self: "Task", stop_type: staticmethod) -> bool:
            result_file_path = os.path.join(
                self.vlog.save_path,
                self.vlog.RESULT_FILENAME
            )
            return_value = method(self, stop_type)
            with open(result_file_path, mode="w", encoding="utf-8") as writable:
                writable.write(str(int(return_value)))
            return return_value
        return wrapper

    def record_handler(method: Callable) -> Callable:
        def wrapper(self: "Task") -> bool:
            record_file_path = os.path.join(
                self.vlog.save_path,
                self.vlog.RECORD_FILENAME
            )
            self.manager.record_start()
            return_value = method(self)
            self.manager.record_stop(record_file_path)
            return return_value
        return wrapper

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
