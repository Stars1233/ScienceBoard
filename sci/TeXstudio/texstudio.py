import sys
import os
import subprocess

from typing import Self
from PIL import Image

sys.dont_write_bytecode = True
from ..base import Manager
from ..vm import VManager


class RawManager(Manager):
    def __init__(self) -> None:
        assert os.system("texstudio --version") == 0
        super().__init__("0.1")

    def __call__(self) -> None:
        raise NotImplementedError

    def __enter__(self) -> Self:
        self.process = subprocess.Popen(
            ["texstudio"],
            stdout=subprocess.PIPE,
            text=True
        )

        Manager.pause()
        return super().__enter__()

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.process.kill()
        super().__exit__(exc_type, exc_value, traceback)

    def screenshot(self) -> Image.Image:
        raise NotImplementedError


class VMManager(VManager):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
