import sys
from typing import List, Iterable

sys.dont_write_bytecode = True
from ..base import Task
from .lean import RawManager
from .format import *


class TaskMixin:
    def __init__(self) -> None:
        raise

    # do not use `@Task._config_handler` here
    def check_config(self: Task) -> None:
        assert len(self.evaluate) > 0


class RawTask(Task, TaskMixin):
    def __init__(
        self,
        config_path: str,
        manager: RawManager,
        *args,
        **kwargs
    ) -> None:
        # to enable Pylance type checker
        assert isinstance(manager, RawManager)
        self.manager = manager
        self.env = None

        super().__init__(config_path, manager, *args, **kwargs)
        self.check_config()

        self.imported: List[str] = []
        self.opened: List[str] = []
        self.initial: Optional[REPLOutputTactic] = None

        # LONG LIVE THE CLOSURE!!
        self.manager.set_headers(lambda _: filter(
            lambda item: item is not None,
            [self.header, self.origin]
        ))

    @property
    def header(self) -> Optional[str]:
        if len(self.imported) == 0 and len(self.opened) == 0:
            return None

        results = ["Headers of the file: "]
        if len(self.imported) > 0:
            results.append(f"import {' '.join(self.imported)}")
        if len(self.opened) > 0:
            results.append(f"open {' '.join(self.opened)}")
        return "\n".join(results)

    @property
    def origin(self) -> Optional[str]:
        if self.initial is None:
            return None

        return "Initial state of the problem: \n" + self.initial.dumps()

    def _import(self, libs: List[str]) -> bool:
        output = self.manager._call({
            "cmd": f"import {' '.join(libs)}",
            "env": self.env
        })
        assert isinstance(output, REPLOutputCommand)

        self.env = output.env
        self.imported.extend(libs)
        return True

    def _open(self, libs: List[str]) -> bool:
        output = self.manager._call({
            "cmd": f"open {' '.join(libs)}",
            "env": self.env
        })
        assert isinstance(output, REPLOutputCommand)

        self.env = output.env
        self.opened.extend(libs)
        return True

    def _query(self, expr) -> bool:
        output = self.manager._call({"cmd": expr, "env": self.env})
        assert isinstance(output, REPLOutputCommand)
        assert output.sorries is not None and len(output.sorries) == 1

        self.initial = REPLOutput.from_sorry(output.sorries[0])
        return True

    @Task._stop_handler
    def eval(self) -> bool:
        return any([item.is_success() for item in self.manager.history])
