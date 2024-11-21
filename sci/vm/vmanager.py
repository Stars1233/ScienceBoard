import sys
import os
import re
import subprocess

from io import BytesIO
from typing import Optional, Union, Iterable, Tuple, Dict, Any
from typing import Self, NoReturn, Callable

import requests
from PIL import Image
from desktop_env.desktop_env import DesktopEnv

sys.dont_write_bytecode
from ..base import Manager
from .. import Prompts
from . import utils

class VManager(Manager):
    VM_PATH = "./vmware"
    INIT_NAME = "sci_bench"
    VERSION_FILE = "__VERSION__"

    def __init__(
        self,
        version: str = "0.1",
        path: Optional[str] = None,
        headless: bool = False,
        a11y_tree_limit: int = 8192
    ) -> None:
        super().__init__(version)

        # version argument should be consistent with vm file
        # no more check required if this assertion pass
        with open(os.path.join(
            os.path.split(path)[0],
            VManager.VERSION_FILE
        ), mode="r", encoding="utf-8") as readble:
            assert(readble.read().strip() == self.version)

        self.path = self.__init_vm() if path is None else path
        assert os.path.exists(self.path)

        assert isinstance(headless, bool)
        self.headless = headless

        # prevent DesktopEnv from loading immediately
        self.env = lambda: DesktopEnv(
            provider_name="vmware",
            region=None,
            path_to_vm=path,
            action_space="pyautogui",
            headless=self.headless,
        )

        assert isinstance(a11y_tree_limit, int)
        self.a11y_tree_limit = a11y_tree_limit

    def __init_vm(self) -> str:
        # TODO: download file to VM_PATH
        # TODO: take snapshot of INIT_NAME
        return "/path/to/vm"

    @staticmethod
    def _env_handler(method: Callable) -> Callable:
        def _env_wrapper(self: "VManager", *args, **kwargs) -> Any:
            assert isinstance(self.env, DesktopEnv)
            return method(self, *args, **kwargs)
        return _env_wrapper

    # hard to use, try OSWorld's service instead
    @_env_handler
    def __vmrun(
        self,
        command: str,
        *args: str,
        tolerance: Iterable[int] = []
    ) -> bool:
        assert isinstance(tolerance, Iterable)
        for return_code in tolerance:
            assert isinstance(return_code, int)
        tolerance = set(tolerance)
        tolerance.add(0)

        assert isinstance(command, str)
        for arg in args:
            assert isinstance(arg, str)

        completed = subprocess.run([
            "vmrun",
            "-T",
            "ws",
            "-gu",
            Prompts.VM_USERNAME,
            "-gp",
            Prompts.VM_PASSWORD,
            command,
            self.path,
            *args
        ], text=True, capture_output=True, encoding="utf-8")

        success = completed.returncode not in tolerance
        if not success:
            self.vlog.error(f"Executing failed on vmrun {command}: {completed.stderr}.")
        return success

    def _run_bash(self, text: str, tolerance: Iterable[int] = []) -> bool:
        assert isinstance(text, str)
        return self.__vmrun(
            "runScriptInGuest",
            "/usr/bin/bash",
            text,
            tolerance=tolerance
        )

    def _request(self, query: str, param: Dict["str", Any]) -> requests.Response:
        request_method, pathname = re.search(r'(GET|POST)(.+)', query).groups()
        request = getattr(requests, request_method.lower())
        url = self.controller.http_server + pathname

        if request == "POST":
            if "header" not in param:
                param["header"] = {}
            if "Content-Type" not in param["header"]:
                param["header"]["Content-Type"] = "application/json"
        return request(url, **param)

    @_env_handler
    def __call__(self, code: str) -> None:
        assert isinstance(code, str)
        self.controller.execute_python_command(code)

    @_env_handler
    def revert(self, snapshot_name: str) -> bool:
        assert isinstance(self.env, DesktopEnv)
        assert isinstance(snapshot_name, str)

        try:
            self.env.snapshot_name = snapshot_name
            self.env.reset()
            return True
        except:
            return False

    def __enter__(self) -> Self:
        self.env: DesktopEnv = self.env()
        self.controller = self.env.controller
        return super().__enter__()

    @_env_handler
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.env.close()
        super().__exit__(exc_type, exc_value, traceback)

    @_env_handler
    @Manager._assert_handler
    def textual(self) -> Optional[str]:
        return self.controller.get_terminal_output()

    @_env_handler
    @Manager._assert_handler
    def screenshot(self) -> Optional[Image.Image]:
        raw_screenshot = self.controller.get_screenshot()
        return Image.open(BytesIO(raw_screenshot))

    @_env_handler
    @Manager._assert_handler
    def a11y_tree(self) -> Optional[str]:
        raw_a11y_tree = self.controller.get_accessibility_tree()
        a11y_tree = utils.linearize(raw_a11y_tree)
        if a11y_tree:
            a11y_tree = utils.trim(a11y_tree, self.a11y_tree_limit)
        return a11y_tree

    @_env_handler
    def set_of_marks(self) -> Union[Tuple[Image.Image, str], NoReturn]:
        # a11y tree consumes more time than screenshot
        # env may change if screenshot is taken in advance
        raw_a11y_tree = self.controller.get_accessibility_tree()
        raw_screenshot = self.controller.get_screenshot()

        # controller does not check nullity
        assert raw_a11y_tree is not None
        assert raw_screenshot is not None

        _, _, som, a11y_tree = utils.tag_screenshot(raw_screenshot, raw_a11y_tree)
        return (
            Image.open(BytesIO(som)),
            utils.trim(a11y_tree, self.a11y_tree_limit)
        )

    @_env_handler
    def record_start(self) -> None:
        self.controller.start_recording()

    @_env_handler
    def record_stop(self, dest_path: str) -> None:
        self.controller.end_recording(dest_path)
