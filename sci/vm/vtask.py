import sys

from typing import List

sys.dont_write_bytecode = True
from ..base import Task
from .vmanager import VManager


class VTask(Task):
    def __init__(
        self,
        config_path: str,
        manager: VManager,
        *args,
        **kwargs
    ) -> None:
        assert isinstance(manager, VManager)

        # TEMP: to enable Pylance type checker
        self.manager = manager

        super().__init__(config_path, manager, *args, **kwargs)
        self.__check_config()

    def __check_config(self) -> None:
        self.snapshot = self.config["snapshot"] \
            if "snapshot" in self.config \
            else VManager.INIT_NAME

    def _init(self) -> bool:
        return self.manager.revert(self.snapshot)

    def _launch(self, program: str, args: List[str]) -> bool:
        return self.manager.run_program(program, *args)

    @Task._stop_handler
    def eval(self) -> bool:
        return True
