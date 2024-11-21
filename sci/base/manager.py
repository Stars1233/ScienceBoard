import sys
import os
import re
import time
import tempfile

from typing import Union, Tuple, Callable, Self, NoReturn, TypeVar
from PIL import Image

sys.dont_write_bytecode = True
from .log import VirtualLog

T = TypeVar("T")

# abstract base class of all apps
# - subclass should include
#   - __init__(): super().__init__() is required
#     - entered: whether app is opened
#     - vlog: virtual global log
#   - __call__(): execute code
#     - no feedback expected if obs_types is None
#     - return value is expected for CLI tasks
#   - __enter__() / __exit__(): open / close app
#   - textual() / screenshot(): one of them for RawManager
#     - for CLI app: textual() only
#     - for GUI Raw: screenshot() only
# - subclass can also include
#   - a11y_tree(): get a11y tree of app
#   - set_of_marks(): get som of app
#   - record_start() / record_stop(): record video for log
class Manager:
    ACTION_INTERVAL = 1

    @staticmethod
    def pause() -> None:        
        time.sleep(Manager.ACTION_INTERVAL)

    def __init__(self, version: str) -> None:
        self.entered = False
        self.vlog = VirtualLog()

        self.__temp_dir = tempfile.TemporaryDirectory()
        self.temp_dir = self.__temp_dir.name

        assert re.match(r'^\d+\.\d+$', version) is not None
        self.version = version

    def __del__(self) -> None:
        self.__temp_dir.cleanup()

    def temp(self, name: str) -> str:
        assert isinstance(name, str)
        return os.path.join(self.temp_dir, name)

    def __call__(self) -> None:
        raise NotImplementedError

    def __enter__(self) -> Self:
        self.entered = True
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.entered = False

    # return whether subclass's screenshot() is implemented
    # basically used by raw manager
    @property
    def is_gui(self) -> None:
        return self.__class__.screenshot != Manager.screenshot

    @staticmethod
    def _assert_handler(
        method: Callable[[Self], T]
    ) -> Callable[[Self], Union[T, NoReturn]]:
        def assert_wrapper(self: Self) -> Union[T, NoReturn]:
            result = method(self)
            assert result is not None
            return result
        return assert_wrapper

    def textual(self) -> Union[str, NoReturn]:
        raise NotImplementedError

    def screenshot(self) -> Union[Image.Image, NoReturn]:
        raise NotImplementedError

    def a11y_tree(self) -> Union[str, NoReturn]:
        raise NotImplementedError

    def set_of_marks(self) -> Union[Tuple[Image.Image, str], NoReturn]:
        raise NotImplementedError

    def record_start(self) -> None:
        self.vlog.warning("record_start() is not implemented.")

    def record_stop(self, dest_path: str) -> None:
        self.vlog.warning(f"record_stop({dest_path}) is not implemented.")
