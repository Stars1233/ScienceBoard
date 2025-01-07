import sys
from typing import List

sys.dont_write_bytecode = True
from ..base import Task
from .lean import RawManager


class TaskMixin:
    def __init__(self) -> None:
        raise

    # do not use `@Task._config_handler`
    def check_config(self: Task) -> None:
        assert len(self.evaluate) > 0


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
        self.env = None

        super().__init__(config_path, manager, *args, **kwargs)
        self.check_config()

    # TEMP: check if they success
    def _import(self, libs: List[str]) -> bool:
        output = self.manager._call({
            "cmd": f"import {' '.join(libs)}",
            "env": self.env
        })
        self.env = output["env"]
        return True

    def _open(self, libs: List[str]) -> bool:
        output = self.manager._call({
            "cmd": f"open {' '.join(libs)}",
            "env": self.env
        })
        self.env = output["env"]
        return True

    def _query(self, expr) -> bool:
        self.manager._call({"cmd": expr, "env": self.env})
        return True

    @Task._stop_handler
    def eval(self) -> bool:
        return self.manager.passed
