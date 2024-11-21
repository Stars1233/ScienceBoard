import sys
import os
import re
import zipfile
import subprocess

from io import BytesIO
from typing import Optional, Union, Iterable, Tuple, Dict, Any
from typing import Self, NoReturn, Callable

import requests
from PIL import Image
from desktop_env.desktop_env import DesktopEnv

sys.dont_write_bytecode
from ..base import Manager
from ..base import GLOBAL_VLOG
from .. import Prompts
from . import utils

class VManager(Manager):
    VM_PATH = "vmware"
    VMX_NAME = "Ubuntu.vmx"
    VERSION_NAME = "__VERSION__"

    INIT_NAME = "sci_bench"
    SERVER_PORT = 5000

    def __init__(
        self,
        version: str = "0.1",
        vm_path: Optional[str] = None,
        headless: bool = False,
        a11y_tree_limit: int = 8192
    ) -> None:
        super().__init__(version)
        self.__vm_path(vm_path)

        assert isinstance(headless, bool)
        self.headless = headless

        # prevent DesktopEnv from loading immediately
        self.env = lambda: DesktopEnv(
            provider_name="vmware",
            region=None,
            path_to_vm=self.path,
            action_space="pyautogui",
            headless=self.headless,
        )

        assert isinstance(a11y_tree_limit, int)
        self.a11y_tree_limit = a11y_tree_limit

    def __is_zip(self, file_path: str):
        assert os.path.exists(file_path)
        with open(file_path, mode="rb") as readble:
            magic_number = readble.read(4)
        return magic_number == b"PK\x03\x04"

    # - check if vm_path is Ubuntu.zip file (and extract)
    # - record vm_path to Ubuntu.vmx file
    def __vm_path(self, vm_path: str):
        if self.__is_zip(vm_path):
            cwd = os.path.join(os.path.abspath("."), VManager.VM_PATH)
            with zipfile.ZipFile(vm_path, "r") as zip_ref:
                GLOBAL_VLOG.info("Start to extract the .zip file...")
                zip_ref.extractall(cwd)
                GLOBAL_VLOG.info("Files were extracted successfully.")
                vm_path = os.path.join(cwd, VManager.VMX_NAME)

        assert os.path.exists(vm_path)
        self.path = vm_path

        # version argument should be consistent with vm file
        # no more check required if this assertion pass
        with open(os.path.join(
            os.path.split(self.path)[0],
            VManager.VERSION_NAME
        ), mode="r", encoding="utf-8") as readble:
            assert(readble.read().strip() == self.version)

        snapshot_detect = self._list_snapshots()
        assert snapshot_detect is not None
        impure_snapshots = snapshot_detect.split("\n")
        if VManager.INIT_NAME not in impure_snapshots:
            GLOBAL_VLOG.input((
                f"Snapshot {VManager.INIT_NAME} will be created automatically; "
                f"press ENTER to continue: "
            ), end="")
            assert self._create_snapshots(VManager.INIT_NAME) is True

    @staticmethod
    def _env_handler(method: Callable) -> Callable:
        def _env_wrapper(self: "VManager", *args, **kwargs) -> Any:
            assert isinstance(self.env, DesktopEnv)
            return method(self, *args, **kwargs)
        return _env_wrapper

    # hard to use, try OSWorld's service instead
    def _vmrun(
        self,
        command: str,
        *args: str,
        tolerance: Iterable[int] = []
    ) -> Tuple[str, bool]:
        assert isinstance(command, str)
        for arg in args:
            assert isinstance(arg, str)

        assert isinstance(tolerance, Iterable)
        for return_code in tolerance:
            assert isinstance(return_code, int)
        tolerance = set(tolerance)
        tolerance.add(0)

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

        success = completed.returncode in tolerance
        if not success:
            self.vlog.fallback().error(
                f"Executing failed on vmrun {command}: {completed.stderr}."
            )
        return (completed.stdout, success)

    def _list_snapshots(self) -> Optional[str]:
        output, success = self._vmrun("listSnapshots")
        return output if success else None

    def _create_snapshots(self, snapshot_name: str) -> bool:
        assert isinstance(snapshot_name, str)
        _, success = self._vmrun("snapshot", snapshot_name)
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
        # query string example: "POST:8080/api/version"
        # correspond to request.post(f"http://{base}:{port}{path}")
        reg_exp = r'(GET|POST)(:\d+)?(.+)'
        request_method, port, pathname = re.search(reg_exp, query).groups()
        if port is None:
            port = f":{VManager.SERVER_PORT}"

        request = getattr(requests, request_method.lower())
        url = self.controller.http_server + port + pathname

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
