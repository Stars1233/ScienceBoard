import sys

sys.dont_write_bytecode = True
from .utils import TypeSort

import sys
import re
import dataclasses

from dataclasses import dataclass

from typing import List
from typing import Callable, Self, NoReturn

sys.dont_write_bytecode = True
from .. import Prompts
from .manager import Manager
from .model import Content
from .utils import TypeSort

RAW = TypeSort.Sort.Raw
VM = TypeSort.Sort.VM

# modify asdict() for class Content
# ref: https://stackoverflow.com/a/78289335
_asdict_inner_actual = dataclasses._asdict_inner
def _asdict_inner(obj, dict_factory):
    if dataclasses._is_dataclass_instance(obj):
        if getattr(obj, "__dict_factory_override__", None):
            user_dict = obj.__dict_factory_override__()
            for key, value in user_dict.items():
                if dataclasses._is_dataclass_instance(value):
                    user_dict[key] = _asdict_inner(value, dict_factory)
            return user_dict
    return _asdict_inner_actual(obj, dict_factory)
dataclasses._asdict_inner = _asdict_inner


# DO NOT DELETE DOCSTRINGS OF EACH PRIMITIVE!
class Primitive:
    WAIT_TIME = 5

    class PlannedTermination(Exception):
        def __init__(self, type: staticmethod) -> None:
            self.type = type

    @staticmethod
    def DONE() -> NoReturn:
        """When you think the task is done, return «DONE»"""
        raise Primitive.PlannedTermination(Primitive.DONE)

    @staticmethod
    def FAIL() -> NoReturn:
        """When you think the task can not be done, return «FAIL», don't easily say «FAIL», try your best to do the task"""
        raise Primitive.PlannedTermination(Primitive.FAIL)

    @staticmethod
    def WAIT() -> None:
        """When you think you have to wait for some time, return «WAIT»"""
        Manager.pause(Primitive.WAIT_TIME)

    @staticmethod
    def TIMEOUT() -> None:
        ...


@dataclass
class CodeLike:
    code: str

    @staticmethod
    def extract_antiquot(content: Content) -> List[Self]:
        occurence = [
            match.group(1).strip()
            for match in re.finditer(
                r'```(?:\w+\s+)?([\w\W]*?)```',
                content.text
            )
        ]
        return [CodeLike(code=code) for code in occurence]

    @staticmethod
    def wrap_antiquot(doc_str: str) -> str:
        return doc_str.replace("«", "```").replace("»", "```")

    @property
    def PRIMITIVE(self) -> List[str]:
        return [
            key for key, value in Primitive.__dict__.items()
            if isinstance(value, staticmethod)
        ]

    def __call__(self, manager: Manager) -> None:
        if self.code in self.PRIMITIVE:
            getattr(Primitive, self.code)()
        else:
            manager(self.code)


class PromptFactory:
    # first section: __intro
    GENERAL_INTRO = "You are an agent which follow my instruction and perform desktop computer tasks as instructed."
    APP_GENERAL = "an application of Ubuntu"
    APP_INCENTIVE = {
        RAW: lambda type, brief_intro: f"You have good knowledge of {type}, {brief_intro}, and assume that your code will run directly in the CLI of {type}.",
        VM: lambda type, brief_intro: f"You have good knowledge of {type}, {brief_intro}, and assume your code will run on a computer controlling the mouse and keyboard."
    }
    OBS_INCENTIVE = lambda obs_descr: f"For each step, you will get an observation of the desktop by {obs_descr}, and you will predict actions of the next step based on that."

    # second section: __general_command
    RETURN_OVERVIEW = {
        RAW: lambda type: f"You are required to use {type} commands to perform the action grounded to the observation. DO NOT use the bash commands or and other codes that {type} itself does not support.",
        VM: lambda _: "You are required to use `pyautogui` to perform the action grounded to the observation, but DO NOT use the `pyautogui.locateCenterOnScreen` function to locate the element you want to operate with since we have no image of the element you want to operate with. DO NOT USE `pyautogui.screenshot()` to make screenshot."
    }
    RETURN_SUPPLEMENT = {
        RAW: lambda type: f"Return one line or multiple lines of {type} CLI commands to perform the action each time, be time efficient.",
        VM: lambda _: "Return one line or multiple lines of python code to perform the action each time, be time efficient. When predicting multiple lines of code, make some small sleep like `time.sleep(0.5);` interval so that the machine could take; Each time you need to predict a complete code, no variables or function can be shared from history"
    }
    RETURN_REGULATION = {
        "antiquot": "You ONLY need to return the code inside a code block, like this:\n```\n# your code here\n```"
    }

    # third section: __special_command
    SPECIAL_OVERVIEW = "Specially, it is also allowed to return the following special code:",

    # fourth section: __warning
    VM_GENERAL = "My computer's password is 'password', feel free to use it when you need sudo rights;"

    # fifth section: __ending
    ENDING_ULTIMATUM = "First give the current observation and previous things we did a short reflection, then RETURN ME THE CODE OR SPECIAL CODE I ASKED FOR. NEVER EVER RETURN ME ANYTHING ELSE."

    def __init__(self, code_style: str) -> None:
        assert hasattr(CodeLike, f"extract_{code_style}")
        self.code_handler: Callable[
            [Content],
            List[CodeLike]
        ] = getattr(CodeLike, f"extract_{code_style}")
        self.code_style = code_style

    def __intro(self, type_sort: TypeSort) -> str:
        brief_intro_name = type_sort.type.upper() + "_IS"
        brief_intro = getattr(Prompts, brief_intro_name, self.APP_GENERAL)

        return "\n".join([
            self.GENERAL_INTRO,
            self.APP_INCENTIVE[type_sort.sort](type_sort.type, brief_intro),
            self.OBS_INCENTIVE("# TODO")
        ])

    def __general_command(self, type_sort: TypeSort) -> str:
        return "..."

    def __special_command(self) -> str:
        return "..."

    def __command(self, type_sort: TypeSort) -> str:
        return "\n\n".join([
            self.__general_command(type_sort),
            self.__special_command()
        ])

    def __warning(self, type_sort: TypeSort) -> str:
        ...

    def __call__(self, type_sort: TypeSort) -> str:
        return "..."
