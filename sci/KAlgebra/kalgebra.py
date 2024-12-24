import sys
from typing import Self

from PIL import Image

sys.dont_write_bytecode
from ..base import Manager

class RawManager(Manager):
    def __init__(self, version: str) -> None:
        super().__init__(version)

    def __call__(self) -> None:
        raise NotImplementedError

    def __enter__(self) -> Self:
        ...
        return super().__enter__()

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        ...
        return super().__exit__(exc_type, exc_value, traceback)

    def screenshot(self) -> Image.Image:
        raise NotImplementedError
