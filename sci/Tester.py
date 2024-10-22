import sys
import os
import traceback

from typing import List, Dict, Set, Iterable

sys.dont_write_bytecode
from . import Model, Agent, Manager, Task
from . import Log

# THESE WILL BE LOOKED-UP BY `globals()`
# DO NOT REMOVE THESE
from .ChimeraX import ChimeraXRawTask

class Tester:
    def __init__(
        self,
        tasks_path: str,
        logs_path: str,
        agents: Dict[str, Agent],
        managers: Dict[str, Manager],
        obs_types: Set[str] = {"screenshot"},
        debug: bool = False,
        sum_log_prefix: str = "SUM@"
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

        # log.error is only called in this file
        # all run-time error / assertion error
        # should be caught in __traverse() & __call()
        # in fact, self.log call inside of tester.__call()
        # should be converted into the form of vlog.info()
        assert isinstance(sum_log_prefix, str)
        self.log = Log()
        self.log.new(self.logs_path, prefix=sum_log_prefix)

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

        assert isinstance(debug, bool)
        self.debug = debug

        self.tasks: List[Task] = []
        self.__traverse()

    def __load(self, config_path: str) -> Task:
        # using nil agent & manager only to load type field
        task_type = Task(
            config_path=config_path,
            agent=Agent(Model("", "", "")),
            manager=Manager()
        ).type

        task_class = globals()[f"{task_type}Task"]

        # assert task_type in self.agents
        # assert task_type in self.managers
        return task_class(
            config_path=config_path,
            manager=self.managers[task_type],
            agent=self.agents[task_type],
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
                    self.log.error(
                        f"Skip failed loading of config {unknown_path}: \n"
                            + traceback.format_exc()
                    )
            else:
                self.__traverse(os.path.join(current_infix, unknown_name))

    def __call__(self):
        for task in self.tasks:
            with self.log(domain=task.ident):
                log_file_path = os.path.join(self.logs_path, task.infix, task.name)
                os.makedirs(log_file_path, exist_ok=True)
                if self.log.switch(log_file_path, clear=True) is False:
                    continue

                try:
                    passed = task()
                    # log.critical() here is not an error info
                    # only to distinguish importance from other loggers
                    self.log.critical(f"PASS of {task.ident}: {passed}")

                except Exception:
                    self.log.error(
                        f"Skip failed testing of task {task.ident}: \n"
                            + traceback.format_exc()
                    )
