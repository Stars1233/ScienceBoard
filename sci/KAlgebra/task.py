import sys
from typing import Dict, Union, Any

sys.dont_write_bytecode = True
from ..base import Task
from ..vm import VTask

from ..base.utils import error_factory
from .kalgebra import RawManager


class TaskMixin:
    def __init__(self) -> None:
        # TODO: this class is not independent: what's needed
        raise

    @Task._config_handler
    def check_config(self, eval_item) -> None:
        # TODO
        assert eval_item["type"] in ("vars", "eqn")
        assert "key" in eval_item
        assert "value" in eval_item

    def _tab(self: Union["RawTask", "VMTask"], index: int) -> bool:
        return self.manager.operate_tab(index)

    @staticmethod
    def _near(left: Any, right: Any) -> bool:
        return abs(float(left) - float(right)) <= 1e-6

    @error_factory(False)
    def _eval_vars(
        self: Union["RawTask", "VMTask"],
        eval_item: Dict[str, Any]
    ) -> bool:
        return TaskMixin._near(
            self.manager.status_vars()[eval_item["key"]],
            eval_item["value"]
        )

    @error_factory(False)
    def _eval_eqn(
        self: Union["RawTask", "VMTask"],
        eval_item: Dict[str, Any]
    ) -> bool:
        return False

    def eval(self: Union["RawTask", "VMTask"]) -> bool:
        for eval_item in self.evaluate:
            eval_type = eval_item["type"]
            eval_func = getattr(self, f"_eval_{eval_type}")
            if not eval_func(eval_item):
                self.vlog.info(f"Evaluation failed at {eval_type} of {eval_item['key']}.")
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
    ...
