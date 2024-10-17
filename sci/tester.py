import sys
import os
import traceback

from dataclasses import dataclass
from typing import List, Dict

sys.dont_write_bytecode
from .agent import Model, Agent
from .manager import Manager

from .task import Task
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
        managers: Dict[str, Manager]
    ) -> None:
        assert os.path.exists(tasks_path)
        assert os.path.isdir(tasks_path)
        self.path = tasks_path

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

        self.task_info: List[TaskInfo] = []
        self.__traverse_tasks()

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

    def __traverse_tasks(self, current_infix: str = ""):
        current_dir_path = os.path.join(self.path, current_infix)
        for unknown_name in os.listdir(current_dir_path):
            unknown_path = os.path.join(current_dir_path, unknown_name)
            if os.path.isfile(unknown_path):
                try:
                    self.task_info.append(TaskInfo(
                        task=self.__load(unknown_path),
                        infix=current_infix
                    ))
                except Exception as err:
                    # TEMP: change to logger
                    print(f"Skip failed loading config {unknown_path}")
                    print(traceback.format_exc())
            else:
                self.__traverse_tasks(os.path.join(current_infix, unknown_name))

    def __traverse_logs(self):
        ...
