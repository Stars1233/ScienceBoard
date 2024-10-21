import sys

from typing import Optional, Any, Self
from PIL import Image

sys.dont_write_bytecode = True
from .log import VirtualLog

# abstract base class of all apps
# - subclass should include
#   - __call__(): execute code, no feedback expected
#   - __enter__() / __exit__(): open / close app
#   - entered: whether app is opened
class Manager:
    def __init__(self) -> None:
        self.entered = False
        self.vlog = VirtualLog()

    def __call__(self) -> None:
        raise NotImplementedError

    def __enter__(self) -> Self:
        self.entered = True
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.entered = False

    def screenshot(self) -> Image.Image:
        raise NotImplementedError

    def a11y_tree(self) -> str:
        raise NotImplementedError

    def set_of_marks(self) -> Image.Image:
        raise NotImplementedError

    def record_start(self) -> None:
        self.vlog.warning("record_start() is not implemented")

    def record_stop(self, dest_path: str) -> None:
        self.vlog.warning("record_stop() is not implemented")
