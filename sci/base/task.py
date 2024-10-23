import sys
import os
import json
import time

from typing import Set, Union, Optional
from typing import Iterable, Callable, NoReturn

sys.dont_write_bytecode = True
from .agent import Agent, Primitive
from .manager import Manager
from .log import Log, VirtualLog

# base class for all tasks
# - subclass should include:
#   - __init__(): just check type and call super.__init__()
#   - __{func}(): functions used by init()
#   - @Task._stop_handler
#     eval(): evaluation of non-general eval-item
# - subclass can also include:
#   - __check_config(): more assertion of config.json
#   - _init(): recover to init states of app
class Task:
    CONFIG_RETRY = 5
    ACTION_INTERVAL = 1
    EARLY_STOP = "stop"
    SORTS = {"Raw", "VM"}

    class PlannedNotImplemented(Exception):
        def __init__(self) -> None:
            ...

    def __init__(
        self,
        config_path: str,
        manager: Optional[Manager] = None,
        agent: Optional[Agent] = None,
        obs_types: Set[str] = {"screenshot"},
        debug: bool = False,
        infix: str = "",
    ) -> None:
        assert isinstance(config_path, str)
        config_path = os.path.expanduser(config_path)
        assert os.path.exists(config_path)
        self.path = config_path

        self.name = os.path.split(self.path)[1].split(".")[0]
        self.config = json.load(open(self.path, mode="r", encoding="utf-8"))
        self.__check_config()

        assert manager is None or isinstance(manager, Manager)
        self.manager = manager

        assert agent is None or isinstance(agent, Agent)
        self.agent = agent

        if self.available:
            assert self.__class__.__name__.startswith(self.sort)

        assert isinstance(obs_types, Iterable)
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

        assert isinstance(infix, str)
        self.infix = infix

        assert isinstance(debug, bool)
        self.debug = debug

        self.vlog = VirtualLog()

    @property
    def available(self) -> bool:
        manager = getattr(self, "manager", None)
        agent = getattr(self, "agent", None)
        return manager is not None and agent is not None

    def __check_config(self) -> None:
        assert "type" in self.config
        self.type = self.config["type"]
        assert isinstance(self.type, str)

        assert "sort" in self.config
        self.sort = self.config["sort"]
        assert self.sort in Task.SORTS

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

    @property
    def ident(self):
        identifier = os.path.join(self.infix, self.name)
        if sys.platform == "win32":
            identifier.replace("\\", "/")
        return identifier

    def _init(self) -> bool:
        self.manager.__exit__(None, None, None)
        time.sleep(Task.ACTION_INTERVAL)
        self.manager.__enter__()
        return True

    def init(self, recover: bool) -> bool:
        assert self.available

        name = lambda func: f"_{self.__class__.__name__}__{func}"
        func = lambda func, **kwargs: getattr(self, name(func))(**kwargs)

        for round_index in range(Task.CONFIG_RETRY):
            feedback = True
            if recover and not self._init():
                continue
            for init_item in self.initialize:
                time.sleep(Task.ACTION_INTERVAL)
                if not func(**init_item):
                    feedback = False
                    break

            if feedback:
                return True
            else:
                continue
        return False

    def _step(self, step_index: int) -> None:
        obs = {
            obs_type: getattr(self.manager, obs_type)()
            for obs_type in self.obs_types
        }
        user_contents = self.agent._step(obs)
        response_message = self.agent(user_contents)
        assert len(response_message.content) == 1

        response_content = response_message.content[0]
        response_codes = self.agent.code_handler(response_content)
        self.vlog.info(f"Response {step_index + 1}/{self.steps}: {response_content.text}")

        for code_like in response_codes:
            time.sleep(Task.ACTION_INTERVAL)
            code_like(self.manager)
        self.vlog.save(
            step_index,
            obs,
            response_codes,
            self.agent.dump_history()
        )

    @Log.record_handler
    def predict(self) -> staticmethod:
        assert self.available

        try:
            self.agent._init(self.instruction)
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
        assert self.available

        eval_index = 0
        while eval_index < len(self.evaluate):
            eval_item = self.evaluate[eval_index]
            if eval_item["type"] != Task.EARLY_STOP:
                eval_index += 1
            elif eval_item["value"] != stop_type.__name__:
                return False
            else:
                del self.evaluate[eval_index]

        if len(self.evaluate) > 0:
            raise Task.PlannedNotImplemented()
        else:
            return True

    def __call(self, recover: bool) -> bool:
        self.vlog.info("Starting initialization.")
        assert self.init(recover=recover), "Fail to initialize the task"
        if self.debug:
            # input value will be converted to stop_type
            # default to TIMEOUT
            primitive_text = self.vlog.input(
                f"Finish task manually: ",
                end=""
            ) or Primitive.TIMEOUT.__name__
            stop_type = getattr(Primitive, primitive_text, Primitive.TIMEOUT)
        else:
            self.vlog.info("Starting prediction.")
            stop_type = self.predict()
        self.vlog.info(f"Starting evaluation with stop type of {stop_type.__name__}.")
        return self.eval(stop_type)

    def __call__(self, recover: Optional[bool] = None) -> bool:
        assert self.available

        self.vlog.info(f"Task: {self.instruction}")
        default = lambda default: default if recover is None else recover
        if not self.manager.entered:
            with self.manager:
                return self.__call(recover=default(True))
        else:
            return self.__call(recover=default(True))
