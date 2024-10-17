import sys
import os
import traceback

from dataclasses import dataclass
from typing import List, Dict

sys.dont_write_bytecode
from . import Model, Agent, Manager, Task
from . import Log

# DO NOT REMOVE THESE
from .ChimeraX.task import ChimeraXTask

@dataclass
class TaskInfo:
    task: Task
    infix: str

class Tester:
    def __init__(
        self,
        tasks_path: str,
        agents: Dict[str, Agent],
        managers: Dict[str, Manager],
        logs_path: str
    ) -> None:
        assert isinstance(tasks_path, str)
        tasks_path = os.path.expanduser(tasks_path)
        assert os.path.exists(tasks_path)
        assert os.path.isdir(tasks_path)
        self.tasks_path = tasks_path

        # agent in agents should not be Agent itself
        assert isinstance(agents, dict)
        for key in agents:
            agent = agents[key]
            assert issubclass(type(agent), Agent)
            assert type(agent) != Agent
        self.agents = agents

        # manager in managers should not be Manager itself
        assert isinstance(managers, dict)
        for key in managers:
            manager = managers[key]
            assert issubclass(type(manager), Manager)
            assert type(manager) != Manager
        self.managers = managers

        assert isinstance(logs_path, str)
        logs_path = os.path.expanduser(logs_path)
        os.makedirs(logs_path, exist_ok=True)
        self.logs_path = logs_path

        self.log = Log()
        self.log.switch(self.logs_path)

        self.tasks_info: List[TaskInfo] = []
        self.__traverse_tasks()
        self.__traverse_logs()

    def __load(self, config_path) -> Task:
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
            agent=self.agents[task_type],
            manager=self.managers[task_type]
        )

    def __traverse_tasks(self, current_infix: str = "") -> None:
        current_dir_path = os.path.join(self.tasks_path, current_infix)
        for unknown_name in os.listdir(current_dir_path):
            unknown_path = os.path.join(current_dir_path, unknown_name)
            if os.path.isfile(unknown_path):
                try:
                    self.tasks_info.append(TaskInfo(
                        task=self.__load(unknown_path),
                        infix=current_infix
                    ))
                except Exception:
                    self.log.error(
                        f"Skip failed loading config {unknown_path}"
                            + "\n"
                            + traceback.format_exc()
                    )
            else:
                self.__traverse_tasks(os.path.join(current_infix, unknown_name))

    def __traverse_logs(self) -> None:
        for task_info in self.tasks_info:
            ...
