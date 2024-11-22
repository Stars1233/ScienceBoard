import sys
import os
import json

from typing import Set, Union, Optional, Any
from typing import Iterable, Callable, NoReturn

sys.dont_write_bytecode = True
from .agent import TypeSort, Agent, Primitive
from .manager import Manager
from .log import Log, VirtualLog
from . import init

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

    class PlannedNotImplemented(Exception):
        def __init__(self) -> None:
            ...

    def __init__(
        self,
        config_path: str,
        manager: Optional[Manager] = None,
        agent: Optional[Agent] = None,
        obs_types: Optional[Set[str]] = None,
        debug: bool = False
    ) -> None:
        assert isinstance(config_path, str)
        config_path = os.path.expanduser(config_path)
        assert os.path.exists(config_path)
        self.path = config_path

        self.name = os.path.split(self.path)[1].split(".")[0]
        self.config = json.load(open(self.path, mode="r", encoding="utf-8"))

        assert manager is None or isinstance(manager, Manager)
        assert agent is None or isinstance(agent, Agent)
        self.manager = manager
        self.agent = agent

        self.__check_config()
        if self.__class__ != Task:
            assert self.version == self.manager.version
        if self.available:
            assert self.__class__.__name__.startswith(self.sort)

        # for RawTask: use textual() for CLI and screenshot() for GUI
        # for VMTask: use pre-defined observation set
        if obs_types is None:
            obs_types = {Manager.screenshot.__name__}
        assert isinstance(obs_types, Iterable)
        assert frozenset(obs_types) in Agent.USER_OPENING
        if self.type_sort.sort == TypeSort.Sort.VM:
            self.obs_types = set(obs_types)
        elif manager is not None:
            self.obs_types = {
                Manager.screenshot.__name__
                if Manager.is_gui
                else Manager.textual.__name__
            }

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
        assert self.sort in TypeSort.Sort._member_names_

        self.type_sort = TypeSort(
            self.type,
            TypeSort.Sort._member_map_[self.sort]
        )

        assert "steps" in self.config
        self.steps = self.config["steps"]
        assert isinstance(self.steps, int)

        assert "instruction" in self.config
        self.instruction = self.config["instruction"]
        assert isinstance(self.instruction, str)

        assert "version" in self.config
        self.version = self.config["version"]
        assert isinstance(self.version, str)

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

    @staticmethod
    def _stop_handler(method: Callable) -> Callable:
        @Log.result_handler
        def _stop_wrapper(self, stop_type: staticmethod) -> bool:
            try:
                return Task.eval(self, stop_type)
            except Task.PlannedNotImplemented:
                return method(self)
        return _stop_wrapper

    @staticmethod
    def _error_handler(method: Callable) -> Callable:
        def _error_wrapper(self, *args) -> bool:
            try:
                return method(self, *args)
            except:
                return False
        return _error_wrapper

    @staticmethod
    def _avail_handler(method: Callable) -> Callable:
        def _avail_wrapper(self: "Task", *args, **kwargs) -> Any:
            assert self.available
            return method(self, *args, **kwargs)
        return _avail_wrapper

    # do not use this method as much as posssible
    # try to customize each manager's own method of resetting
    def _init(self) -> bool:
        try:
            self.manager.__exit__(None, None, None)
            Manager.pause()
            self.manager.__enter__()
            return True
        except:
            return False

    # find local `func` first
    # then find `raw_func` or `vm_func` in .base.init
    # according to self.sort (in {"Raw", "VM"})
    @_avail_handler
    def init(self) -> bool:
        local_name = lambda func: f"_{func}"
        global_name = lambda func: f"{self.sort.lower()}_{func}"

        def func(func: str, wait: int = 0, **kwargs):
            result = getattr(
                self,
                local_name(func),
                getattr(init, global_name(func))
            )(**kwargs)
            Manager.pause(wait)
            return result

        # try `Task.CONFIG_RETRY` times
        # trigger assertion error if all fail
        for _ in range(Task.CONFIG_RETRY):
            feedback = True
            # set to init state from second try
            # if _init() failed, goto next iteration
            if not self._init():
                continue

            # try every init item in config file
            # if error occurred / do not return True
            # then stop init and retry in next iteration
            for init_item in self.initialize:
                Manager.pause()
                succeed = False
                try:
                    succeed = func(**init_item)
                finally:
                    if not succeed:
                        feedback = False
                        break

            # if any of item fails
            # feed back would not be True
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

        # special cases: SoM -> SoM + A11y Tree
        if Manager.set_of_marks.__name__ in obs:
            som, a11y_tree = obs[Manager.set_of_marks.__name__]
            obs[Manager.a11y_tree.__name__] = a11y_tree
            obs[Manager.set_of_marks.__name__] = som

        user_contents = self.agent._step(obs)
        response_message = self.agent(user_contents)
        assert len(response_message.content) == 1

        response_content = response_message.content[0]
        response_codes = self.agent.code_handler(response_content)
        self.vlog.info(f"Response {step_index + 1}/{self.steps}: {response_content.text}")

        for code_like in response_codes:
            code_like(self.manager)
            Manager.pause()

        self.vlog.save(
            step_index,
            obs,
            response_codes,
            self.agent.dump_history()
        )

    @_avail_handler
    @Log.record_handler
    def predict(self) -> staticmethod:
        try:
            self.agent._init(self.instruction, self.type_sort)
            for step_index in range(self.steps):
                self._step(step_index)
        except Primitive.PlannedTermination as early_stop:
            return early_stop.type
        return Primitive.TIMEOUT

    # in case Task().eval() is derectly called
    # if eval() of Task's subclass is called
    # result output will be written twice sometimes
    @_avail_handler
    @Log.result_handler
    def eval(self, stop_type: staticmethod) -> Union[bool, NoReturn]:
        eval_index = 0

        while eval_index < len(self.evaluate):
            eval_item = self.evaluate[eval_index]
            if eval_item["type"] != Task.EARLY_STOP:
                eval_index += 1
            elif eval_item["value"] != stop_type.__name__:
                self.vlog.info(f"Evaluation failed at stop type.")
                return False
            else:
                del self.evaluate[eval_index]

        if len(self.evaluate) > 0:
            raise Task.PlannedNotImplemented()
        else:
            return True

    def __call(self) -> bool:
        self.vlog.info("Starting initialization.")
        assert self.init(), "Fail to initialize the task"
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

    @_avail_handler
    def __call__(self) -> bool:
        self.vlog.info(f"\033[1mTask: {self.instruction}\033[0m")
        if not self.manager.entered:
            with self.manager:
                return self.__call()
        else:
            return self.__call()
