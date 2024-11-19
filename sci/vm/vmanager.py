import sys

from io import BytesIO
from typing import Optional, Union, Tuple, Self, NoReturn

from PIL import Image
from desktop_env.desktop_env import DesktopEnv

sys.dont_write_bytecode
from ..base import Manager
from .som import tag_screenshot

class VManager(Manager):
    def __init__(
        self,
        # TODO
    ) -> None:
        super().__init__()

        self.env = DesktopEnv(
            path_to_vm="...",
            action_space="pyautogui",
            screen_size=(1920, 1080),
            headless=False,
            require_a11y_tree=True,
            require_terminal=False,
        )
        self.controller = self.env.controller

    def __call__(self) -> None:
        ...

    def __enter__(self) -> Self:
        return super().__enter__()

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        super().__exit__(exc_type, exc_value, traceback)

    # TODO: linearize a11y_tree()
    # TODO: VM's `with` waste lots of time, how to optimize?
    # TODO: to disable OSWorld's logging
    @Manager._assert_handler
    def textual(self) -> Optional[str]:
        return self.controller.get_terminal_output()

    @Manager._assert_handler
    def screenshot(self) -> Optional[Image.Image]:
        raw_screenshot = self.controller.get_screenshot()
        return Image.open(BytesIO(raw_screenshot))

    @Manager._assert_handler
    def a11y_tree(self) -> Optional[str]:
        return self.controller.get_accessibility_tree()

    def set_of_marks(self) -> Union[Tuple[Image.Image, str], NoReturn]:
        # a11y tree consumes more time than screenshot
        # env may change if screenshot is taken in advance
        raw_a11y_tree = self.a11y_tree()

        # getting raw screenshot content
        # controller does not check nullity
        raw_screenshot = self.controller.get_screenshot()
        assert raw_screenshot is not None

        _, _, som, a11y_tree = tag_screenshot(raw_screenshot, raw_a11y_tree)
        return (Image.open(BytesIO(som)), a11y_tree)

    def record_start(self) -> None:
        self.controller.start_recording()

    def record_stop(self, dest_path: str) -> None:
        self.controller.end_recording(dest_path)
