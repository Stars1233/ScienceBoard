import sys
import os
import traceback

from dataclasses import dataclass
from typing import List, Dict, Set, Optional
from typing import Iterable, Callable

sys.dont_write_bytecode
from . import Agent, Manager, Task
from . import Log

# THESE WILL BE LOOKED-UP BY `globals()`
# DO NOT REMOVE THESE
from . import ChimeraX

@dataclass
class Counter:
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    ignored: int = 0

    # suggested functions usage:
    # counter._pass()
    # counter._fail()
    # counter._skip()
    # counter._ignore()
    def __getattr__(self, attr: str) -> Optional[Callable]:
        for field in self.__dataclass_fields__:
            if attr[0] == "_" and field.startswith(attr[1:]):
                def func(self):
                    setattr(self, field, getattr(self, field) + 1)
                return func.__get__(self)
        return None

    def __str__(self) -> str:
        total = self.passed + self.failed + self.skipped + self.ignored
        return (
            f"{total} total tested: "
            f"{self.passed} passed, "
            f"{self.failed} failed, "
            f"{self.skipped} skipped, "
            f"{self.ignored} ignored."
        )

class Tester:
    def __init__(
        self,
        tasks_path: str,
        logs_path: str,
        managers: Dict[str, Manager],
        agents: Dict[str, Agent],
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

        # log.critical is only called in this file
        # all run-time error / assertion error
        # should be caught in __traverse() & __call()
        # in fact, self.log call inside of tester.__call()
        # should be converted into the form of vlog.info()
        self.log = Log()
        self.log.new(self.logs_path, prefix=Log.SUM_LOG_PREFIX)

        # agent in agents should not be Agent itself
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
        for unknown_name in os.listdir(current_dir_path):
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

    # log.critical() here is not an error info
    # only to distinguish importance from other loggers
    def __call__(self):
        local_counter = Counter()
        for task in self.tasks:
            with self.log(domain=task.ident):
                log_file_path = os.path.join(self.logs_path, task.ident)
                os.makedirs(log_file_path, exist_ok=True)
                if not self.log.switch(log_file_path, ignore=self.ignore):
                    local_counter._ignore()
                    self.log.critical("Task already finished; ignored.")
                    continue

                try:
                    passed = task()
                    local_counter._pass() if passed else local_counter._fail()
                    self.log.critical(f"Task finished with passed={passed}.")

                except Exception:
                    local_counter._skip()
                    self.log.critical(
                        f"Task testing failed; skipped\n"
                            + traceback.format_exc()
                    )
        self.log.critical(local_counter)
