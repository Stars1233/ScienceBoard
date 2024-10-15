import sys
import re
import json

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
            for key_name in eval_item:
                assert key_name in ("find", "key", "value")
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
    def __eval_states(self, current_states, eval_item):
        find = eval_item["find"] if "find" in eval_item else None
        key = eval_item["key"]
        value = eval_item["value"]

        raw_key = None
        if key.startswith("lambda"):
            key = eval(key)

        # find meta_key by key-value pair using find(key)
        # process meta_key to raw_key using key(meta_key)
        # type of find: (str, Any) -> bool
        # type of key: str -> str
        if find is not None:
            find = eval(find)
            meta_keys = list(filter(find, current_states.items()))
            raw_key = key(meta_keys[0][0])

        # find raw_key directly using key(key)
        # type of key: str -> bool
        elif hasattr(key, "__call__"):
            raw_keys = list(filter(key, current_states.keys()))
            raw_key = raw_keys[0]

        # key itself is raw_key
        # type of key: str
        else:
            raw_key = key

        # get targeted raw_value by raw_key
        raw_value = current_states[raw_key]
        if not isinstance(raw_value, str):
            raw_value = json.dumps(raw_value)
        return re.search(value, raw_value) is not None

    def exec_eval(self) -> bool:
        current_states = self.manager.states_dump()
        for eval_item in self.evaluate:
            if not self.__eval_states(current_states, eval_item):
                return False
        return True
