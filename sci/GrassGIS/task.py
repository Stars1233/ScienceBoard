import sys
from typing import Dict, Union, Callable

sys.dont_write_bytecode = True
from ..base import Task
from ..vm import VTask

from ..base.utils import error_factory
from .grass import RawManager, VMManager


class TaskMixin:
    def __init__(self) -> None:
        # this class is not independent: manager, evaluate, vlog needed
        raise

    @Task._config_handler
    def check_config(self, eval_item) -> None:
        assert eval_item["type"] == "info"
        assert "key" in eval_item
        assert "value" in eval_item

    def _gcmd(self: Union["RawTask", "VMTask"], cmd, kwargs) -> bool:
        return self.manager.operate_gcmd(cmd, kwargs)

    def _map(
        self: Union["RawTask", "VMTask"],
        grassdb: str,
        location: str,
        mapset: str
    ) -> bool:
        return self.manager.operate_map(grassdb, location, mapset)

    def _layer(
        self: Union["RawTask", "VMTask"],
        query: Dict[str, str]
    ) -> bool:
        return self.manager.operate_layer(query)

    @error_factory(False)
    def eval(self: Union["RawTask", "VMTask"]) -> bool:
        info = self.manager.status_dump()
        for eval_item in self.evaluate:
            hkey: Callable = lambda info: info[eval_item["key"]]
            pred: Callable = lambda left, right: left == right

            if hasattr(key_eval := eval(eval_item["key"]), "__call__"):
                hkey = key_eval
            if "pred" in eval_item:
                pred = eval(eval_item["pred"])

            if not pred(hkey(info), eval_item["value"]):
                return False
        return True


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

    def _init(self) -> bool:
        # TEMP: do nothing
        return True

    @Task._stop_handler
    def eval(self) -> bool:
        # MRO: RawTask -> Task -> TaskMixin -> object
        return super(Task, self).eval()


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
        # MRO: VMTask -> VTask -> Task -> TaskMixin -> object
        return super(Task, self).eval()
