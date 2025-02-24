import sys
from typing import Dict, Union, Any

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
        assert eval_item["type"] in ("vars", "eqns")
        numeral = (int, float)

        assert "key" in eval_item
        key = eval_item["key"]
        if not isinstance(key, str):
            assert isinstance(key, list)
            for item in key:
                assert isinstance(item, list)
                assert len(item) in (2, 3)
                for sub_item in item:
                    assert type(sub_item) in numeral

        assert "value" in eval_item
        value = eval_item["value"]
        if type(value) not in numeral:
            assert isinstance(value, dict)
            for sub_key, sub_value in value.items():
                assert isinstance(sub_key, str)
                assert type(sub_value) in (bool, str)

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
