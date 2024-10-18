import sys
import os
import json

from typing import Callable, Union, Optional, NoReturn

sys.dont_write_bytecode = True
from .agent import Agent, Primitive
from .manager import Manager

# base class for all tasks, subclass should include
# - init(): parse & execute init part of config
# - eval(): parse & execute eval part of config
class Task:
    CONFIG_RETRY = 5
    EARLY_STOP = "stop"

    def __init__(self, config_path: str, agent: Agent, manager: Manager) -> None:
        assert isinstance(config_path, str)
        config_path = os.path.expanduser(config_path)
        assert os.path.exists(config_path)
        self.path = config_path

        self.name = os.path.split(self.path)[1].split(".")[0]
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

        assert "steps" in self.config
        self.steps = self.config["steps"]
        assert isinstance(self.steps, int)

        assert "instruction" in self.config
        self.instruction = self.config["instruction"]
        assert isinstance(self.instruction, str)

        assert "initialize" in self.config
        self.initialize = self.config["initialize"]
        assert isinstance(self.initialize, list)
        for init_item in self.initialize:
            assert isinstance(init_item, dict)
            assert "func" in init_item
            assert isinstance(init_item["func"], str)

        assert "evaluate" in self.config
        self.evaluate = self.config["evaluate"]
        assert isinstance(self.evaluate, list)
        for eval_item in self.evaluate:
            assert isinstance(eval_item, dict)
            assert "type" in eval_item
            if eval_item["type"] == Task.EARLY_STOP:
                assert "value" in eval_item
                assert isinstance(eval_item["value"], str)

    def _error_handler(method: Callable) -> Callable:
        def wrapper(self, *args) -> bool:
            try:
                return method(self, *args)
            except:
                return False
        return wrapper

    def _init(self) -> bool:
        self.manager.__exit__(None, None, None)
        self.manager.__enter__()
        return True

    def init(self, recover: bool) -> bool:
        init = lambda func, **kwargs: getattr(
            self,
            f"_{self.__class__.__name__}__{func}"
        )(**kwargs)
        for round_index in range(Task.CONFIG_RETRY):
            if recover and not self._init():
                continue
            success_list = [
                init(**init_item)
                for init_item in self.initialize
            ]
            if all(success_list):
                return True
        return False

    def predict(self) -> staticmethod:
        try:
            for step_index in range(self.steps):
                user_contents = self.agent._step_user_contents(self)
                response_message = self.agent(user_contents)
                response_code = self.agent.code_handler(response_message.content[0])
                response_code(self.manager)
        except Primitive.PlannedTermination as early_stop:
            return early_stop.type
        return Primitive.TIMEOUT

    def _stop_handler(method: Callable) -> Callable:
        def wrapper(self, stop_type: staticmethod) -> bool:
            try:
                return Task.eval(self, stop_type)
            except NotImplementedError:
                return method(self)
        return wrapper

    def eval(self, stop_type: staticmethod) -> Union[bool, NoReturn]:
        for eval_index, eval_item in enumerate(self.evaluate):
            if eval_item["type"] == Task.EARLY_STOP:
                # eval_item won't be deleted in `for` for ref_count ≠ 0
                del self.evaluate[eval_index]
                if eval_item["value"] != stop_type.__name__:
                    return False

        if len(self.evaluate) > 0:
            raise NotImplementedError
        else:
            return True

    def __call(self, recover: bool) -> bool:
        assert self.init(recover=recover), "Fail to initialize task of {self.path}"
        stop_type = self.predict()
        return self.eval(stop_type)

    def __call__(self, recover: Optional[bool] = None) -> bool:
        default = lambda default: default if recover is None else recover
        if not self.manager.entered:
            with self.manager:
                return self.__call(recover=default(True))
        else:
            return self.__call(recover=default(True))
