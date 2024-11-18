import sys
from desktop_env.desktop_env import DesktopEnv

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

    def __call__(self) -> None:
        ...

    def __enter__(self) -> Self:
        return super().__enter__()

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        super().__exit__(None, None, None)

    def textual(self) -> str:
        raise NotImplementedError

    def screenshot(self) -> Image.Image:
        raise NotImplementedError

    def a11y_tree(self) -> str:
        raise NotImplementedError

    def set_of_marks(self) -> Image.Image:
        raise NotImplementedError

    def record_start(self) -> None:
        self.env.controller.start_recording()

    def record_stop(self, dest_path: str) -> None:
        self.env.controller.end_recording(dest_path)
