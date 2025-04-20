import sys
import os

from typing import Union, Dict, Any

sys.dont_write_bytecode = True
from ..base import Task
from ..vm import VTask

from ..base.utils import error_factory
from .texstudio import RawManager, VMManager


class TaskMixin:
    def __init__(self) -> None:
        # this class is not independent: manager, evaluate, vlog needed
        raise

    def origin(self: Union["RawTask", "VMTask"], path: str) -> str:
        return os.path.join(
            self.path.replace(".json", ""),
            os.path.split(path)[1]
        )

    @Task._config_handler
    def check_config(self, eval_item) -> None:
        if eval_item["type"] == "compile":
            assert "file" in eval_item
        else:
            assert eval_item["type"] == "file"

        assert "path" in eval_item


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

        super().__init__(config_path, manager, *args, **kwargs)
        self.check_config()

    @Task._stop_handler
    @error_factory(False)
    def eval(self) -> bool:
        raise NotImplementedError


class VMTask(VTask, TaskMixin):
    def __init__(
        self,
        config_path: str,
        manager: VMManager,
        *args,
        **kwargs
    ) -> None:
        # to enable Pylance type checker
        assert isinstance(manager, VMManager)
        self.manager = manager

        super().__init__(config_path, manager, *args, **kwargs)
        self.check_config()

    def __read(self, path: str) -> str:
        with open(self.origin(path), mode="r", encoding="utf-8") as readable:
            return readable.read()

    def _drop(self, path: str) -> bool:
        return self.manager.write_file(
            self.origin(path),
            self.__read(path)
        )

    @error_factory(False)
    def _eval_file(self: "VMTask", eval_item: Dict[str, Any]) -> bool:
        before = self.__read(eval_item["path"])
        after = self.manager.read_file(eval_item["path"])
        after = after.replace(eval_item["source"], eval_item["target"])
        return before == after

    @error_factory(False)
    def _eval_compile(self: "VMTask", eval_item: Dict[str, Any]) -> bool:
        response = self.manager._request("POST/tex/check", {
            "json": {
                "path": eval_item["path"],
                "file": eval_item["file"]
            }
        })
        return response.json()["pass"]

    @Task._stop_handler
    @error_factory(False)
    def eval(self) -> bool:
        for eval_item in self.evaluate:
            eval_type = eval_item["type"]
            eval_func = getattr(self, f"_eval_{eval_type}")
            if not eval_func(eval_item):
                self.vlog.info(f"Evaluation failed at {eval_type} of {eval_item['key']}.")
                return False
        return True
