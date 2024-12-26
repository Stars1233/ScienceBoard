import sys
import os
import subprocess

from typing import Self

import requests
from PIL import Image

sys.dont_write_bytecode
from ..base import Manager
from ..vm import VManager


class ManagerMixin:
    def __init__(self, ip: str, port: int) -> None:
        # legality is not checked due to inner usage
        self.base_url = f"http://{ip}:{port}"

    def status_version(self) -> str:
        return requests.get(self.base_url + "/version").text

    def status_vars(self) -> str:
        return requests.get(self.base_url + "/vars").json()

    def operate_tab(self, index: int) -> bool:
        assert isinstance(index, int)
        assert index >= 0 and index < 4
        return requests.post(self.base_url + "/tab", json=index).text == "OK"


class RawManager(Manager, ManagerMixin):
    def __init__(
        self,
        bin_path: str,
        lib_path: str,
        version: str = "0.2",
        port: int = 8000
    ) -> None:
        super().__init__(version)

        assert port in range(1024, 65536)
        self.port = port

        # MRO: RawManager -> Manager -> ManagerMixin -> Object
        super(Manager, self).__init__("localhost", port)

        assert os.path.isfile(bin_path)
        self.bin_path = bin_path

        assert os.path.isdir(lib_path)
        self.lib_path = lib_path

    def __call__(self) -> None:
        raise NotImplementedError

    def __enter__(self) -> Self:
        env = os.environ.copy()
        env["LD_LIBRARY_PATH"] = self.lib_path
        self.process = subprocess.Popen(
            [self.bin_path, str(self.port)],
            env=env,
            stdout=subprocess.PIPE,
            text=True
        )

        Manager.pause()
        assert self.status_version() == self.version
        return super().__enter__()

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.process.kill()
        super().__exit__(exc_type, exc_value, traceback)

    def screenshot(self) -> Image.Image:
        raise NotImplementedError


class VMManager(VManager, ManagerMixin):
    ...
