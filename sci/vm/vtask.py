import sys

sys.dont_write_bytecode = True
from ..base import Task
from .vmanager import VManager

# base class for all tasks
# - subclass should include:
#   - __init__(): just check type and call super.__init__()
#   - __{func}(): functions used by init()
#   - @Task._stop_handler
#     eval(): evaluation of non-general eval-item
# - subclass can also include:
#   - __check_config(): more assertion of config.json
#   - _init(): recover to init states of app
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
