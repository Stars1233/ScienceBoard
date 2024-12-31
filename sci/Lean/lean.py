import sys

sys.dont_write_bytecode
from ..base import Manager


class RawManager(Manager):
    def __init__(self, version: str) -> None:
        super().__init__(version)
