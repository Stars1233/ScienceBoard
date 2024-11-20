import sys
import os
import inspect
import traceback

from dataclasses import dataclass

from typing import Union, List, Set
from typing import Iterable, Callable

sys.dont_write_bytecode
from . import TypeSort, Model, Agent
from . import Manager, Task
from . import Log, VirtualLog
from . import Presets


@dataclass
class Counter:
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    ignored: int = 0
    vlog: VirtualLog = VirtualLog()

    def _pass(self):
        self.passed += 1
        self.vlog.info("\033[1mTask finished with passed=TRUE.\033[0m")

    def _fail(self):
        self.failed += 1
        self.vlog.info("\033[1mTask finished with passed=FALSE.\033[0m")

    def _skip(self):
        self.skipped += 1
        self.vlog.error("Task testing failed; skipped.\n" + traceback.format_exc())

    def _ignore(self):
        self.ignored += 1
        self.vlog.info("Task already finished; ignored.")
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
        self.vlog.info(self.__repr__())


# Automata only receive keyword args from Model and Agent
class Automata:
    def __init__(self, **kwargs) -> None:
        model_params = list(Model.__dataclass_fields__.keys())
        agent_params = list(inspect.signature(Agent).parameters)
        for key in kwargs:
            assert key in model_params or key in agent_params

        self.model_args = {
            key: value for key, value in kwargs.items()
            if key in model_params
        }

        self.agent_args = {
            key: value for key, value in kwargs.items()
            if key in agent_params
        }

    def __call__(self) -> Agent:
        model = Model(**self.model_args)
        return Agent(model=model, **self.agent_args)


class TaskInfo:
    def __init__(self, task: Task, infix: str = "") -> None:
        assert isinstance(task, Task)
        self.task = task

        assert isinstance(infix, str)
        self.infix = infix

    @property
    def ident(self):
        identifier = os.path.join(self.infix, self.task.name)
        if sys.platform == "win32":
            identifier.replace("\\", "/")
        return identifier

    def __lt__(self, __value: "TaskInfo") -> bool:
        left, right = self.task, __value.task
        return left.sort < right.sort or \
            (left.sort == right.sort and left.type < right.type)

    def __repr__(self) -> str:
        return f"{self.ident}: {self.task.sort}.{self.task.type}"

    def __call__(self) -> bool:
        return self.task()


class TaskGroup:
    def __init__(self, raw: List[TaskInfo]) -> None:
        assert isinstance(raw, list)
        self.groups: List[List[TaskInfo]] = []

        last_info = None
        for task_info in raw:
            assert isinstance(task_info, TaskInfo)
            if last_info is not None \
                and task_info.task.type_sort == last_info.task.type_sort:
                self.groups[-1].append(task_info)
            else:
                self.groups.append([task_info])
            last_info = task_info

    def __check(self):
        for group in self.groups:
            assert len(group) > 0
            for task_info in group:
                assert group[0].task.manager == task_info.task.manager

    def __call__(self):
        self.__check()
        for group in self.groups:
            with group[0].task.manager:
                for task_info in group:
                    yield task_info


class Tester:
    def __init__(
        self,
        tasks_path: str,
        logs_path: str,
        automata: Automata,
        obs_types: Set[str] = {Manager.screenshot.__name__},
        ignore: bool = True,
        debug: bool = False,
        optimize: bool = True
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

        assert isinstance(automata, Automata)
        self.agent = automata()
        self.agent.vlog.set(self.log)

        # manager in managers should not be Manager itself
        self.modules = Presets.spawn_modules()
        self.manager_args = Presets.spawn_managers()
        self.managers = {}

        assert isinstance(obs_types, Iterable)
        self.obs_types = obs_types

        assert isinstance(ignore, bool)
        self.ignore = ignore

        assert isinstance(debug, bool)
        self.debug = debug

        assert isinstance(optimize, bool)
        self.optimize = optimize

        self.task_info: List[TaskInfo] = []
        self.__traverse()
        self.task_group = TaskGroup(sorted(self.task_info))

    def __manager(self, type_sort: TypeSort):
        if type_sort in self.managers:
            return self.managers[type_sort]

        manager_class = getattr(
            self.modules[type_sort.type],
            type_sort(Manager.__name__)
        )
        manager = manager_class(**self.manager_args[type_sort])
        self.managers[type_sort] = manager
        manager.vlog.set(self.log)
        return manager

    def __load(self, config_path: str) -> Task:
        # using nil agent & manager only to load type field
        type_sort = Task(config_path=config_path).type_sort
        task_class = getattr(
            self.modules[type_sort.type],
            type_sort(Task.__name__)
        )

        return task_class(
            config_path=config_path,
            manager=self.__manager(type_sort),
            agent=self.agent,
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
                    new_task.vlog.set(self.log)
                    self.task_info.append(TaskInfo(new_task, infix=current_infix))
                except Exception:
                    error_info = "Config loading failed; skipped: " \
                        + unknown_path \
                        + "\n" \
                        + traceback.format_exc()
                    self.log.error(error_info)
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
        for task_info in self.task_group() if self.optimize else self.task_info:
            with self.log(
                base_path=self.logs_path,
                ident=task_info.ident,
                ignore=self.ignore
            ) as result_exist:
                if result_exist:
                    counter._ignore()
                    continue
                try:
                    counter._pass() if task_info() else counter._fail()
                except Exception:
                    counter._skip()
