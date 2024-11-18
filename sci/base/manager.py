import sys

from typing import Self
from PIL import Image

sys.dont_write_bytecode = True
from .log import VirtualLog

# abstract base class of all apps
# - subclass should include
#   - __init__(): super().__init__() is required
#     - entered: whether app is opened
#     - vlog: virtual global log
#   - __call__(): execute code
#     - no feedback expected if obs_types is None
#     - return value is expected for CLI tasks
#   - __enter__() / __exit__(): open / close app
# - subclass can also include
#   - screenshot(): take screenshot of app
#   - a11y_tree(): get a11y tree of app
#   - set_of_marks(): get som of app
#   - record_start() / record_stop(): record video for log
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

    # return whether subclass's screenshot() is implemented
    # basically used by raw manager
    def is_gui(self) -> None:
        return self.__class__.screenshot != Manager.screenshot

    def textual(self) -> str:
        raise NotImplementedError

    def screenshot(self) -> Image.Image:
        raise NotImplementedError

    def a11y_tree(self) -> str:
        raise NotImplementedError

    def set_of_marks(self) -> Image.Image:
        raise NotImplementedError

    def record_start(self) -> None:
        self.vlog.warning("record_start() is not implemented.")

    def record_stop(self, dest_path: str) -> None:
        self.vlog.warning("record_stop() is not implemented.")
