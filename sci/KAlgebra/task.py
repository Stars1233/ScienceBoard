import sys

sys.dont_write_bytecode = True
from ..base import Task
from .kalgebra import RawManager


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

        super().__init__(config_path, manager, *args, **kwargs)
        self.__check_config()

    def __check_config(self) -> None:
        ...

    @Task._stop_handler
    def eval(self) -> bool:
        return False
