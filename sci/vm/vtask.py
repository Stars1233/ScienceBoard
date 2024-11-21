import sys

from typing import List, Dict, Union, Any, Callable

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

        # to enable Pylance type checker
        self.manager = manager

        super().__init__(config_path, manager, *args, **kwargs)
        self.__check_config()

    def __check_config(self) -> None:
        self.snapshot = self.config["snapshot"] \
            if "snapshot" in self.config \
            else VManager.INIT_NAME

    def _init(self) -> bool:
        return self.manager.revert(self.snapshot)

    # OSWorld's request does not check success
    # rewrite requests to make up this flaw
    @staticmethod
    def _request_factory(query: str):
        def _request_decorator(method: Callable) -> Callable:
            def _request_wrapper(self: "VTask", *args, **kwargs) -> bool:
                param: Dict["str", Any] = method(self, *args, **kwargs)
                try:
                    response = self.manager._request(query, param)
                    succeed = response.status_code == 200
                    if not succeed:
                        self.vlog.error(f"Failed when requesting {query}: {response.status_code}")
                    return succeed
                except Exception as err:
                    self.vlog.error(f"Error when requesting {query}: {err}")
                    return False
            return _request_wrapper
        return _request_decorator

    @_request_factory("POST/setup/launch")
    def _launch(self, command: Union[str, List[str]], shell: bool = False) -> Dict:
        isinstance(command, list)
        if isinstance(command, list):
            for part in command:
                assert isinstance(part, str)
        else:
            assert isinstance(command, str)

        assert isinstance(shell, bool)
        return {
            "json": {
                "command": command,
                "shell": shell
            }
        }
