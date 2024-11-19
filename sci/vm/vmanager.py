import sys
from desktop_env.desktop_env import DesktopEnv

from io import BytesIO
from typing import Optional, Self

from PIL import Image

sys.dont_write_bytecode
from ..base import Manager

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

    # TODO: VM's `with` waste lots of time, how to optimize?
    # TODO: to disable OSWorld's logging
    @Manager._assert_handler
    def textual(self) -> Optional[str]:
        return self.controller.get_terminal_output()

    @Manager._assert_handler
    def screenshot(self) -> Optional[Image.Image]:
        screenshot = self.controller.get_screenshot()
        return Image.open(BytesIO(screenshot))

    @Manager._assert_handler
    def a11y_tree(self) -> Optional[str]:
        return self.controller.get_accessibility_tree()

    @Manager._assert_handler
    def set_of_marks(self) -> Optional[Image.Image]:
        return "..."

    def record_start(self) -> None:
        self.controller.start_recording()

    def record_stop(self, dest_path: str) -> None:
        self.controller.end_recording(dest_path)
