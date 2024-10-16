import os
import json

from typing import Callable

class Task:
    CONFIG_RETRY = 5

    def __init__(self, config_path: str) -> None:
        assert os.path.exists(config_path)
        self.path = config_path
        self.config = json.load(open(self.path, mode="r", encoding="utf-8"))
        self._check_config()

    def _check_config(self) -> None:
        assert "type" in self.config
        self.type = self.config["type"]
        assert isinstance(self.type, str)

        assert "instruction" in self.config
        self.instruction = self.config["instruction"]
        assert isinstance(self.instruction, str)

        assert "initialize" in self.config
        self.initialize = self.config["initialize"]
        assert isinstance(self.initialize, list)
        for init_item in self.initialize:
            assert isinstance(init_item, dict)

        assert "evaluate" in self.config
        self.evaluate = self.config["evaluate"]
        assert isinstance(self.evaluate, list)
        for eval_item in self.evaluate:
            assert isinstance(eval_item, dict)

    def exec_init(self) -> bool:
        raise NotImplementedError

    def _error_handler(method: Callable):
        def wrapper(self, *args):
            try:
                return method(self, *args)
            except:
                return False
        return wrapper

    def exec_eval(self) -> bool:
        raise NotImplementedError

    def _test(self) -> bool:
        self.exec_init()
        input(self.instruction)
        return self.exec_eval()

    def __call__(self) -> bool:
        assert hasattr(self, "manager")
        manager = getattr(self, "manager")
        if not manager.entered:
            with manager:
                return self._test()
        else:
            return self._test()
