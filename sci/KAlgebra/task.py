import sys
from typing import Union

sys.dont_write_bytecode = True
from ..base import Task
from ..vm import VTask
from .kalgebra import RawManager


class TaskMixin:
    @Task._config_handler
    def check_config(self, eval_item) -> None:
        # TODO
        assert eval_item["type"] in ("vars", "eqn")
        assert "key" in eval_item
        assert "value" in eval_item

    def eval(self: Union["RawTask", "VMTask"]) -> bool:
        return False

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
        super(Task, self).eval()


class VMTask(VTask, TaskMixin):
    ...
