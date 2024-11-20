import sys

from io import BytesIO
from typing import Optional, Union, Tuple
from typing import Self, NoReturn, Callable

from PIL import Image
from desktop_env.desktop_env import DesktopEnv

sys.dont_write_bytecode
from ..base import Manager
from . import utils

class VManager(Manager):
    def __init__(
        self,
        a11y_tree_limit: int = 1024
    ) -> None:
        super().__init__()

        # lazy loading
        self.env = lambda: DesktopEnv(
            path_to_vm="/media/PJLAB\wangyian/Data/repo/osworld/vmware_vm_data/Ubuntu.vmx",
            action_space="pyautogui",
            headless=False
        )

        assert isinstance(a11y_tree_limit, int)
        self.a11y_tree_limit = a11y_tree_limit

    @staticmethod
    def _env_handler(method: Callable) -> Callable:
        def env_wrapper(self: Self):
            assert isinstance(self.env, DesktopEnv)
            return method(self)
        return env_wrapper

    @_env_handler
    def __call__(self, code: str) -> None:
        assert isinstance(code, str)
        self.controller.execute_python_command(code)

    @_env_handler
    def revert(self, snapshot_name: str) -> bool:
        assert isinstance(self.env, DesktopEnv)
        assert isinstance(snapshot_name, str)

        self.env.snapshot_name = snapshot_name
        self.env.reset()

    def __enter__(self) -> Self:
        self.env: DesktopEnv = self.env()
        self.controller = self.env.controller
        return super().__enter__()

    @_env_handler
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.env.close()
        super().__exit__(exc_type, exc_value, traceback)

    @Manager._assert_handler
    @_env_handler
    def textual(self) -> Optional[str]:
        return self.controller.get_terminal_output()

    @Manager._assert_handler
    @_env_handler
    def screenshot(self) -> Optional[Image.Image]:
        raw_screenshot = self.controller.get_screenshot()
        return Image.open(BytesIO(raw_screenshot))

    @Manager._assert_handler
    @_env_handler
    def a11y_tree(self) -> Optional[str]:
        raw_a11y_tree = self.controller.get_accessibility_tree()
        return utils.trim(utils.linearize(raw_a11y_tree), self.a11y_tree_limit)

    @_env_handler
    def set_of_marks(self) -> Union[Tuple[Image.Image, str], NoReturn]:
        # a11y tree consumes more time than screenshot
        # env may change if screenshot is taken in advance
        raw_a11y_tree = self.a11y_tree()

        # getting raw screenshot content
        # controller does not check nullity
        raw_screenshot = self.controller.get_screenshot()
        assert raw_screenshot is not None

        _, _, som, a11y_tree = utils.tag_screenshot(raw_screenshot, raw_a11y_tree)
        return (Image.open(BytesIO(som)), a11y_tree)

    @_env_handler
    def record_start(self) -> None:
        self.controller.start_recording()

    @_env_handler
    def record_stop(self, dest_path: str) -> None:
        self.controller.end_recording(dest_path)
