import sys
import os
import subprocess

from typing import Self

import requests
from PIL import Image

sys.dont_write_bytecode
from ..base import Manager

class RawManager(Manager):
    def __init__(
        self,
        bin_path: str,
        lib_path: str,
        version: str = "0.2"
    ) -> None:
        super().__init__(version)

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
            self.bin_path,
            env=env,
            stdout=subprocess.PIPE,
            text=True
        )

        version = requests.get("http://localhost:8080/version").text
        assert version == self.version
        return super().__enter__()

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.process.kill()
        return super().__exit__(exc_type, exc_value, traceback)

    def screenshot(self) -> Image.Image:
        raise NotImplementedError
