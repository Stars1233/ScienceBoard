import sys
from typing import List

sys.dont_write_bytecode = True
from ..base import Task
from .lean import RawManager


class RawTask(Task):
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

    # TEMP: check if they success
    def _import(self, libs: List[str]) -> bool:
        self.manager({
            "cmd": f"import {' '.join(libs)}",
            "env": self.env
        })
        self.env = self.manager.history[-1]["env"]
        return True

    def _open(self, libs: List[str]) -> bool:
        self.manager({
            "cmd": f"open {' '.join(libs)}",
            "env": self.env
        })
        self.env = self.manager.history[-1]["env"]
        return True

    def _query(self, expr) -> bool:
        self.manager({"cmd": expr, "env": self.env})
        return True

    @Task._stop_handler
    def eval(self) -> bool:
        return self.manager.passed
