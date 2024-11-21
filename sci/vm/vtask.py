import sys

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
        super().__init__(config_path, manager, *args, **kwargs)
        self.__check_config()

    def __check_config(self) -> None:
        ...

    def _init(self) -> bool:
        return True

    @Task._stop_handler
    def eval(self) -> bool:
        return True
