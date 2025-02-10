import sys
import os

from typing import Union, Dict, Any

sys.dont_write_bytecode = True
from ..base import Task
from ..vm import VTask
from .texstudio import RawManager, VMManager


class TaskMixin:
    def __init__(self) -> None:
        # this class is not independent: manager, evaluate, vlog needed
        raise

    @Task._config_handler
    def check_config(self, eval_item) -> None:
        assert eval_item["type"] == "file"
        assert "path" in eval_item

    def eval(
        self: Union["RawTask", "VMTask"],
        eval_item: Dict[str, Any],
        file_path: str
    ) -> bool:
        return open(file_path, mode="r").read() == "1"


class RawTask(Task, TaskMixin):
    def __init__(
        self,
        config_path: str,
        manager: RawManager,
        *args,
        **kwargs
    ) -> None:
        # to enable Pylance type checker
        assert isinstance(manager, RawManager)
        self.manager = manager

        super().__init__(config_path, manager, *args, **kwargs)
        self.check_config()

    @Task._stop_handler
    def eval(self) -> bool:
        for eval_item in self.evaluate:
            # MRO: VMTask -> VTask -> Task -> TaskMixin -> object
            if not super(Task, self).eval(eval_item, eval_item["path"]):
                return False
        return True


class VMTask(VTask, TaskMixin):
    def __init__(
        self,
        config_path: str,
        manager: VMManager,
        *args,
        **kwargs
    ) -> None:
        # to enable Pylance type checker
        assert isinstance(manager, VMManager)
        self.manager = manager

        super().__init__(config_path, manager, *args, **kwargs)
        self.check_config()

    @Task._stop_handler
    def eval(self) -> bool:
        for eval_item in self.evaluate:
            guest_file = eval_item["path"]
            local_file = self.temp(os.path.split(guest_file)[1])
            assert self._vmrun("CopyFileFromGuestToHost", guest_file, local_file)[1]

            # MRO: VMTask -> VTask -> Task -> TaskMixin -> object
            if not super(Task, self).eval(eval_item, local_file):
                return False
        return True
