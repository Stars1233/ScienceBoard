import sys
import re
import time
import dataclasses

from enum import Enum
from dataclasses import dataclass, asdict

from typing import Optional, List, Dict, Set
from typing import Callable, Any, Self, NoReturn

from PIL import Image
from requests import Response

sys.dont_write_bytecode = True
from .manager import Manager
from .log import VirtualLog
from .model import Content, TextContent, ImageContent
from .model import Message, Model
from . import utils
from .. import Prompts

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


@dataclass
class TypeSort:
    class Sort(Enum):
        Raw = 0
        VM = 1

    type: str
    sort: Sort

    def __str__(self) -> str:
        return f"{self.type}_{self.sort.name}"

    def __repr__(self) -> str:
        if self.sort == TypeSort.Sort.VM:
            return self.sort.name
        else:
            return f"{self.sort.name}:{self.type}"

    def __call__(self, postfix: str) -> Any:
        return self.sort.name + postfix

    # crucial for hash comparison
    def __eq__(self, __value: "TypeSort") -> bool:
        return self.__repr__() == __value.__repr__()

    def __hash__(self) -> int:
        return hash(self.__repr__())


class Primitive:
    class PlannedTermination(Exception):
        def __init__(self, type: staticmethod) -> None:
            self.type = type

    @staticmethod
    def DONE() -> NoReturn:
        raise Primitive.PlannedTermination(Primitive.DONE)

    @staticmethod
    def FAIL() -> NoReturn:
        raise Primitive.PlannedTermination(Primitive.FAIL)

    @staticmethod
    def WAIT() -> None:
        time.sleep(Agent.WAIT_TIME)

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


class Overflow:
    @staticmethod
    def openai_gpt(response: Response) -> bool:
        return response.status_code != 200 \
            and response.json()["error"]["code"] == "context_length_exceeded"

    @staticmethod
    def openai_lmdeploy(response: Response) -> bool:
        return Model._access_openai(response).content == ""


class Agent:
    WAIT_TIME = 5

    SYSTEM_INST = lambda inst: f"You are asked to complete the following task: {inst}"
    USER_FLATTERY = "What's the next step that you will do to help with the task?"
    USER_OPENING: Dict[Set[str], str] = {
        frozenset({
            Manager.textual.__name__
        }): "Given the terminal output as below:\n{textual}\n",
        frozenset({
            Manager.screenshot.__name__
        }): "Given the screenshot as below. ",
        frozenset({
            Manager.a11y_tree.__name__
        }): "Given the info from accessibility tree as below:\n{a11y_tree}\n",
        frozenset({
            Manager.a11y_tree.__name__,
            Manager.set_of_marks.__name__
        }): "Given the tagged screenshot and info from accessibility tree as below:\n{a11y_tree}\n",
        frozenset({
            Manager.screenshot.__name__,
            Manager.a11y_tree.__name__
        }): "Given the screenshot and info from accessibility tree as below:\n{a11y_tree}\n"
    }

    def __init__(
        self,
        model: Model,
        code_style: str = "antiquot",
        overflow_style: Optional[str] = None,
        context_window: int = 3
    ) -> None:
        assert isinstance(model, Model)
        self.model = model

        assert hasattr(CodeLike, f"extract_{code_style}")
        self.code_handler: Callable[
            [Content],
            List[CodeLike]
        ] = getattr(CodeLike, f"extract_{code_style}")
        self.code_style = code_style

        assert overflow_style is None or hasattr(Overflow, overflow_style)
        self.overflow_handler: Optional[Callable[[Response], bool]] = None \
            if overflow_style is None \
            else getattr(Overflow, overflow_style)
        self.overflow_style = overflow_style

        assert isinstance(context_window, int)
        assert context_window >= 0
        self.context_window = context_window

        self.vlog = VirtualLog()

    def _init(self, inst: str, type_sort: Optional[TypeSort] = None) -> None:
        prompt_name = f"{self.code_style}_{type_sort}".upper()
        system_inst = getattr(Prompts, prompt_name, self.SYSTEM_INST)

        self.system_message: Message = self.model.message(
            role="system",
            content=[TextContent(system_inst(inst).strip())]
        )
        self.context: List[Message] = []

    # crucial: obs here may not be the same as in Task
    # e.g. Task.obs_types=SoM -> Agent._step(obs={SoM, A11yTree})
    def _step(self, obs: Dict[str, Any]) -> List[Content]:
        textual = utils.getitem(obs, Manager.textual.__name__, None)
        a11y_tree = utils.getitem(obs, Manager.a11y_tree.__name__, None)

        opening = self.USER_OPENING[frozenset(obs.keys())].format(
            textual=textual,
            a11y_tree=a11y_tree
        )
        contents = [TextContent(opening + Agent.USER_FLATTERY)]

        images = [item for _, item in obs.items() if isinstance(item, Image.Image)]
        contents += [ImageContent(image) for image in images]
        return contents

    def __dump(self, context_count: int) -> List[Message]:
        return [
            self.system_message,
            *self.context[-context_count:]
        ]

    def dump_payload(self, context_length: int) -> Dict:
        return [
            asdict(message)
            for message in self.__dump(context_length * 2 + 1)
        ]

    def dump_history(self) -> Dict:
        return [
            message._asdict(self.context_window)
            for message in self.__dump(len(self.context))
        ]

    def __call__(
        self,
        contents: List[Content],
        shorten: int = 0
    ) -> Message:
        assert hasattr(self, "context"), "Call Agent.init() first"

        assert isinstance(contents, list)
        for content in contents:
            assert isinstance(content, Content)

        context_length = self.context_window - shorten
        self.context.append(self.model.message(role="user", content=contents))
        response = self.model(messages=self.dump_payload(context_length))

        if response.status_code != 200:
            self.vlog.warning(f"Getting response code of {response.status_code}.")

        is_overflow = False if self.overflow_handler is None \
            else self.overflow_handler(response)

        if is_overflow and shorten < self.context_window:
            return self(contents, shorten + 1)
        assert not is_overflow, f"Tokens overflow when calling {self.model.model_name}"

        response_message = self.model.access(response, context_length)
        self.context.append(response_message)
        return response_message
