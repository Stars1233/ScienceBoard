import sys
import re
import json

from typing import List, Tuple, Dict, Callable, Any

sys.dont_write_bytecode = True
from ..base import Task
from .chimerax import RawManager

class RawTask(Task):
    def __init__(
        self,
        config_path: str,
        manager: RawManager,
        *args,
        **kwargs
    ) -> None:
        assert isinstance(manager, RawManager)
        super().__init__(config_path, manager, *args, **kwargs)
        self.__check_config()

    def __check_config(self) -> None:
        assert "version" in self.config
        self.version = self.config["version"]
        assert isinstance(self.version, str)
        assert self.version == self.manager.version

        for eval_item in self.evaluate:
            if eval_item["type"] == Task.EARLY_STOP:
                continue

            assert eval_item["type"] in ("states", "info")
            assert "key" in eval_item
            assert "value" in eval_item

            for key_name in eval_item:
                assert key_name in ("type", "find", "key", "value")

                if key_name == "find":
                    assert eval_item["type"] == "states"

                if key_name == "value" and eval_item["type"] == "info":
                    assert isinstance(eval_item[key_name], list)
                    for sub_item in eval_item[key_name]:
                        assert isinstance(sub_item, str)
                else:
                    assert isinstance(eval_item[key_name], str)

    def _init(self) -> bool:
        _, code = self.manager._call("close")
        return code and self.manager.clear_history()

    def __open(self, name: str) -> bool:
        _, code = self.manager._call(f"open {name}")
        return code

    def __turn(self, axis: str, angle: int) -> bool:
        _, code = self.manager._call(f"turn {axis} {angle}")
        return code

    @Task._error_handler
    def __eval_states(
        self,
        eval_item: Dict[str, Any],
        current_states: Dict[str, Any]
    ) -> bool:
        find: str = eval_item["find"] if "find" in eval_item else None
        key: str = eval_item["key"]
        value: str = eval_item["value"]

        raw_key = None
        if key.startswith("lambda"):
            key: Callable[[str], Any] = eval(key)

        # find meta_key by key-value pair using find(key)
        # process meta_key to raw_key using key(meta_key)
        # type of find: (str, Any) -> bool
        # type of key: str -> str
        if find is not None:
            find: Callable[[Tuple[Any]], bool] = eval(find)
            meta_keys: List[Tuple[Any]] = list(filter(find, current_states.items()))
            raw_key: str = key(meta_keys[0][0])

        # find raw_key directly using key(key)
        # type of key: str -> bool
        elif hasattr(key, "__call__"):
            raw_keys: List[str] = list(filter(key, current_states.keys()))
            raw_key: str = raw_keys[0]

        # key itself is raw_key
        # type of key: str
        else:
            raw_key: str = key

        # get targeted raw_value by raw_key
        raw_value: Any = current_states[raw_key]
        if not isinstance(raw_value, str):
            raw_value: str = json.dumps(raw_value)
        return re.search(value, raw_value) is not None

    @Task._error_handler
    def __eval_info(
        self,
        eval_item: Dict[str, Any],
        current_states: Dict[str, Any]
    ) -> bool:
        key = eval_item["key"]
        value = eval_item["value"]

        log_message, _ = self.manager._call(f"info {key}")
        nested_logs = [log.strip().split("\n") for log in log_message]
        info_list = [log for logs in nested_logs for log in logs if log != ""]
        return set(info_list) == set(value)

    @Task._stop_handler
    def eval(self) -> bool:
        current_states = self.manager.states_dump()
        for eval_item in self.evaluate:
            eval_type = eval_item["type"]
            method_name = f"_{self.__class__.__name__}__eval_{eval_type}"
            eval_func = getattr(self, method_name)
            if not eval_func(eval_item, current_states):
                return False
        return True
