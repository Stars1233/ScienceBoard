import sys
import os
import json

from typing import Set, Union, Optional
from typing import Callable, NoReturn

sys.dont_write_bytecode = True
from .agent import Agent, Primitive
from .manager import Manager
from .log import Log, VirtualLog

# base class for all tasks
# - subclass should include:
#   - __{func}(): functions used by init()
#   - @Task._stop_handler eval(): evaluation of non-stop
# - subclass can also include:
#   - __check_config(): more assertion of config.json
#   - _init(): recover to init states of app
class Task:
    CONFIG_RETRY = 5
    EARLY_STOP = "stop"

    class PlannedNotImplemented(Exception):
        def __init__(self) -> None:
            ...

    def __init__(
        self,
        config_path: str,
        agent: Agent,
        manager: Manager,
        obs_types: Set[str] = {"screenshot"}
    ) -> None:
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

        for obs_type in obs_types:
            assert obs_type in (
                Manager.screenshot.__name__,
                Manager.a11y_tree.__name__,
                Manager.set_of_marks.__name__
            )

        # SoM has the highest priority
        if Manager.set_of_marks.__name__ in obs_types:
            assert len(obs_types) == 1
        self.obs_types = obs_types

        self.vlog = VirtualLog()

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

    def _step(self, step_index: int) -> None:
        obs = {
            obs_type: getattr(self.manager, obs_type)()
            for obs_type in self.obs_types
        }
        user_contents = self.agent.step_user_contents(obs)
        response_message = self.agent(user_contents)
        assert len(response_message.content) == 1

        response_content = response_message.content[0]
        response_codes = self.agent.code_handler(response_content)
        for code_like in response_codes:
            code_like(self.manager)
        self.vlog.save(step_index, obs, response_codes)

    @Log.record_handler
    def predict(self) -> staticmethod:
        try:
            for step_index in range(self.steps):
                self._step(step_index)
        except Primitive.PlannedTermination as early_stop:
            return early_stop.type
        return Primitive.TIMEOUT

    def _stop_handler(method: Callable) -> Callable:
        @Log.result_handler
        def wrapper(self, stop_type: staticmethod) -> bool:
            try:
                return Task.eval(self, stop_type)
            except Task.PlannedNotImplemented:
                return method(self)
        return wrapper

    def _error_handler(method: Callable) -> Callable:
        def wrapper(self, *args) -> bool:
            try:
                return method(self, *args)
            except:
                return False
        return wrapper

    # in case Task().eval() is derectly called
    # if eval() of Task's subclass is called
    # result output will be written twice sometimes
    @Log.result_handler
    def eval(self, stop_type: staticmethod) -> Union[bool, NoReturn]:
        for eval_index, eval_item in enumerate(self.evaluate):
            if eval_item["type"] == Task.EARLY_STOP:
                # eval_item won't be deleted in `for` for ref_count ≠ 0
                del self.evaluate[eval_index]
                if eval_item["value"] != stop_type.__name__:
                    return False

        if len(self.evaluate) > 0:
            raise Task.PlannedNotImplemented()
        else:
            return True

    def __call(self, recover: bool) -> bool:
        assert self.init(recover=recover), "Fail to initialize the task"
        stop_type = self.predict()
        return self.eval(stop_type)

    def __call__(self, recover: Optional[bool] = None) -> bool:
        default = lambda default: default if recover is None else recover
        if not self.manager.entered:
            with self.manager:
                return self.__call(recover=default(True))
        else:
            return self.__call(recover=default(True))
