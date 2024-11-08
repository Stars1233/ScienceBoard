import sys

from typing import Self

from PIL import Image

sys.dont_write_bytecode
from ..base import Manager

class VManager(Manager):
    def __init__(self) -> None:
        super().__init__()

    def __call__(self) -> None:
        ...

    def __enter__(self) -> Self:
        return super().__enter__()

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        super().exit(None, None, None)

    def screenshot(self) -> Image.Image:
        raise NotImplementedError

    def a11y_tree(self) -> str:
        raise NotImplementedError

    def set_of_marks(self) -> Image.Image:
        raise NotImplementedError

    def record_start(self) -> None:
        raise NotImplementedError

    def record_stop(self, dest_path: str) -> None:
        raise NotImplementedError
