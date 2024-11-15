import sys
import os
import traceback

from dataclasses import dataclass
from typing import List, Dict, Set
from typing import Iterable, Callable

sys.dont_write_bytecode
from . import Agent, Manager, Task, Log, VirtualLog
from . import Presets

# THESE WILL BE LOOKED-UP BY `globals()`
# DO NOT REMOVE THESE
from . import ChimeraX

@dataclass
class Counter:
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    ignored: int = 0
    vlog: VirtualLog = VirtualLog()

    # log.critical() here is not any error info
    # only to distinguish importance from other loggers
    def _pass(self):
        self.passed += 1
        self.vlog.critical("\033[1mTask finished with passed=TRUE.\033[0m")

    def _fail(self):
        self.failed += 1
        self.vlog.critical("\033[1mTask finished with passed=FALSE.\033[0m")

    def _skip(self):
        self.skipped += 1
        self.vlog.critical("Task testing failed; skipped.\n" + traceback.format_exc())

    def _ignore(self):
        self.ignored += 1
        self.vlog.critical("Task already finished; ignored.")
        self.vlog.register(Log.delete)

    def __str__(self) -> str:
        total = self.passed + self.failed + self.skipped + self.ignored
        return (
            f"{total} total tested: "
            f"{self.passed} passed, "
            f"{self.failed} failed, "
            f"{self.skipped} skipped, "
            f"{self.ignored} ignored."
        )

    def __repr__(self) -> str:
        return "\033[1m" + self.__str__() + "\033[0m"

    def callback(self) -> None:
        self.vlog.critical(self.__repr__())


class Tester:
    def __init__(
        self,
        tasks_path: str,
        logs_path: str,
        agents: Dict[str, Agent],
        managers: Dict[str, Manager] = Presets.spawn_managers(),
        obs_types: Set[str] = {"screenshot"},
        ignore: bool = True,
        debug: bool = False
    ) -> None:
        assert isinstance(tasks_path, str)
        tasks_path = os.path.expanduser(tasks_path)
        assert os.path.exists(tasks_path)
        assert os.path.isdir(tasks_path)
        self.tasks_path = tasks_path

        # process log first
        assert isinstance(logs_path, str)
        logs_path = os.path.expanduser(logs_path)
        os.makedirs(logs_path, exist_ok=True)
        self.logs_path = logs_path

        # all run-time error / assertion error
        # should be caught in __traverse() & __call()
        # in fact, self.log call inside of tester.__call()
        # should be converted into the form of vlog.info()
        self.log = Log()

        # agent in agents should be Agent
        assert isinstance(agents, dict)
        for key in agents:
            agent = agents[key]
            assert isinstance(agent, Agent)
            agent.vlog.set(self.log)
        self.agents = agents

        # manager in managers should not be Manager itself
        assert isinstance(managers, dict)
        for key in managers:
            manager = managers[key]
            assert issubclass(type(manager), Manager)
            assert type(manager) != Manager
            manager.vlog.set(self.log)
        self.managers = managers

        assert isinstance(obs_types, Iterable)
        self.obs_types = obs_types

        assert isinstance(ignore, bool)
        self.ignore = ignore

        assert isinstance(debug, bool)
        self.debug = debug

        self.tasks: List[Task] = []
        self.__traverse()

    def __load(self, config_path: str) -> Task:
        # using nil agent & manager only to load type field
        nil_task = Task(config_path=config_path)
        task_type = nil_task.type
        task_sort = nil_task.sort

        task_class = getattr(globals()[task_type], task_sort + "Task")

        # assert task_type in self.agents
        # assert task_type in self.managers
        return task_class(
            config_path=config_path,
            manager=self.managers[f"{task_type}:{task_sort}"],
            agent=self.agents[f"{task_type}:{task_sort}"],
            obs_types=self.obs_types,
            debug=self.debug
        )

    def __traverse(self, current_infix: str = "") -> None:
        current_dir_path = os.path.join(self.tasks_path, current_infix)
        for unknown_name in sorted(os.listdir(current_dir_path)):
            unknown_path = os.path.join(current_dir_path, unknown_name)
            if os.path.isfile(unknown_path):
                try:
                    new_task = self.__load(unknown_path)
                    new_task.infix = current_infix
                    new_task.vlog.set(self.log)
                    self.tasks.append(new_task)
                except Exception:
                    self.log.critical(
                        f"Config loading failed; skipped: {unknown_path}\n"
                            + traceback.format_exc()
                    )
            else:
                self.__traverse(os.path.join(current_infix, unknown_name))

    @staticmethod
    def _log_handler(method: Callable) -> Callable:
        def log_wrapper(self: "Tester"):
            local_counter = Counter()
            local_counter.vlog.set(self.log)
            self.log.trigger(
                self.logs_path,
                prefix=self.log.SUM_LOG_PREFIX,
                dependent=False
            )
            method(self, local_counter)
            self.log.callback()
            local_counter.callback()
        return log_wrapper

    # there is no need to pass counter
    # as decorator has done all for it
    @_log_handler
    def __call__(self, counter: Counter):
        for task in self.tasks:
            with self.log(
                base_path=self.logs_path,
                ident=task.ident,
                ignore=self.ignore
            ) as result_exist:
                if result_exist:
                    counter._ignore()
                    continue
                try:
                    counter._pass() if task() else counter._fail()
                except Exception:
                    counter._skip()
