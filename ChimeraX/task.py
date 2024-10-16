import sys
import re
import json

from typing import List, Tuple, Dict, Callable, Any

sys.dont_write_bytecode = True
from task import Task
from .chimerax import ChimeraX

class ChimeraXTask(Task):
    AgentType = ChimeraX

    def __init__(self, config_path: str, manager: ChimeraX) -> None:
        super().__init__(config_path)

        assert isinstance(manager, ChimeraX)
        self.manager = manager
        self.__check_config()

    def __check_config(self) -> None:
        assert "version" in self.config
        self.version = self.config["version"]
        assert isinstance(self.version, str)
        assert self.version == self.manager.version

        for init_item in self.initialize:
            assert "func" in init_item
            assert isinstance(init_item["func"], str)

        for eval_item in self.evaluate:
            assert "type" in eval_item
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

    def __recover(self) -> bool:
        return self.manager._run("close") and self.manager.clear_history()

    def __open(self, name: str) -> bool:
        return self.manager._run(f"open {name}")

    def __exec(self, cmd: str) -> bool:
        return self.manager._run(cmd)

    def exec_init(self) -> bool:
        init = lambda func, **kwargs: getattr(self, f"_ChimeraXTask__{func}")(**kwargs)
        for round_index in range(Task.CONFIG_RETRY):
            self.__recover()
            success_list = [init(**init_item) for init_item in self.initialize]
            if all(success_list):
                return True
        return False

    @Task._error_handler
    def __eval_states(self, eval_item: Dict[str, Any], current_states: Dict[str, Any]):
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
    def __eval_info(self, eval_item: Dict[str, Any], current_states: Dict[str, Any]):
        key = eval_item["key"]
        value = eval_item["value"]
        info_list = self.manager.run(f"info {key}")[0].strip().split("\n")
        return set(info_list) == set(value)

    def exec_eval(self) -> bool:
        current_states = self.manager.states_dump()
        for eval_item in self.evaluate:
            eval_func = getattr(self, f"_ChimeraXTask__eval_{eval_item['type']}")
            if not eval_func(eval_item, current_states):
                return False
        return True
