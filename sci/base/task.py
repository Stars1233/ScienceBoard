import sys
import os
import json

from typing import Callable

sys.dont_write_bytecode = True
from .agent import Agent
from .manager import Manager

# base class for all tasks, subclass should include
# - init(): parse & execute init part of config
# - eval(): parse & execute eval part of config
class Task:
    CONFIG_RETRY = 5

    def __init__(self, config_path: str, agent: Agent, manager: Manager) -> None:
        assert isinstance(config_path, str)
        config_path = os.path.expanduser(config_path)
        assert os.path.exists(config_path)
        self.path = config_path
        self.config = json.load(open(self.path, mode="r", encoding="utf-8"))
        self.__check_config()

        assert isinstance(agent, Agent)
        self.agent = agent

        assert isinstance(manager, Manager)
        self.manager = manager

    def __check_config(self) -> None:
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

    def init(self) -> bool:
        raise NotImplementedError

    def _error_handler(method: Callable) -> Callable:
        def wrapper(self, *args) -> bool:
            try:
                return method(self, *args)
            except:
                return False
        return wrapper

    def eval(self) -> bool:
        raise NotImplementedError

    def __call(self) -> bool:
        assert self.init(), "Fail to initialize task of {self.path}"
        self.agent(self)
        return self.eval()

    def __call__(self) -> bool:
        if not self.manager.entered:
            with self.manager:
                return self.__call()
        else:
            return self.__call()
