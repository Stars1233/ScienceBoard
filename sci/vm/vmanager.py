import sys
from desktop_env.desktop_env import DesktopEnv

from typing import Self

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
        super().__exit__(None, None, None)

    @Manager._assert_handler
    def textual(self) -> str:
        self.controller.get_terminal_output()

    @Manager._assert_handler
    def screenshot(self) -> Image.Image:
        self.controller.get_screenshot()

    @Manager._assert_handler
    def a11y_tree(self) -> str:
        self.controller.get_accessibility_tree()

    @Manager._assert_handler
    def set_of_marks(self) -> Image.Image:
        return "..."

    def record_start(self) -> None:
        self.controller.start_recording()

    def record_stop(self, dest_path: str) -> None:
        self.controller.end_recording(dest_path)
