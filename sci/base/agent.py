import sys

from dataclasses import asdict
from typing import Optional, List, Dict, Set
from typing import Callable, Any

from PIL import Image
from requests import Response

sys.dont_write_bytecode = True
from . import utils
from .manager import Manager
from .log import VirtualLog
from .model import Content, TextContent, ImageContent
from .model import Message, Model
from .utils import TypeSort
from .prompt import CodeLike, Primitive, PromptFactory


class Overflow:
    @staticmethod
    @utils.error_factory(False)
    def openai_gpt(response: Response) -> bool:
        return response.json()["error"]["code"] == "context_length_exceeded"

    @staticmethod
    @utils.error_factory(False)
    def openai_lmdeploy(response: Response) -> bool:
        return Model._access_openai(response).content[0].text == ""

    @staticmethod
    @utils.error_factory(False)
    def anthropic(response: Response) -> bool:
        return response.json()["error"]["type"] == "request_too_large"


class Agent:
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
        overflow_style: Optional[str] = None,
        context_window: int = 3,
        code_style: str = "antiquot"
    ) -> None:
        assert isinstance(model, Model)
        self.model = model

        assert overflow_style is None or hasattr(Overflow, overflow_style)
        self.overflow_handler: Optional[Callable[[Response], bool]] = None \
            if overflow_style is None \
            else getattr(Overflow, overflow_style)
        self.overflow_style = overflow_style

        assert isinstance(context_window, int)
        assert context_window >= 0
        self.context_window = context_window

        assert hasattr(CodeLike, f"extract_{code_style}")
        self.code_style = code_style
        self.code_handler: Callable[
            [Content],
            List[CodeLike]
        ] = getattr(CodeLike, f"extract_{code_style}")

        self.prompt_factory = PromptFactory(code_style)
        self.vlog = VirtualLog()

    def _init(self, inst: str, type_sort: Optional[TypeSort] = None) -> None:
        # prompt_name = f"{self.code_style}_{type_sort}".upper()
        # system_inst = getattr(Prompts, prompt_name, self.SYSTEM_INST)
        system_inst = self.prompt_factory(type_sort)

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
        shorten: int = 0,
        retry: int = 3
    ) -> Message:
        assert hasattr(self, "context"), "Call Agent.init() first"
        assert retry > 0, f"Max reties exceeded when calling {self.model.model_name}"

        assert isinstance(contents, list)
        for content in contents:
            assert isinstance(content, Content)

        context_length = self.context_window - shorten
        self.context.append(self.model.message(role="user", content=contents))
        response = self.model(messages=self.dump_payload(context_length))

        is_overflow = False if self.overflow_handler is None \
            else self.overflow_handler(response)

        if is_overflow and context_length > 0:
            self.vlog.error(
                f"Overflow detected when requesting {self.model.model_name}; "
                f"set context_window={context_length - 1}."
            )
            return self(contents, shorten + 1, retry)
        assert not is_overflow, f"Unsolvable overflow when requesting {self.model.model_name}"

        response_message = self.model.access(response, context_length)
        if response_message is None:
            self.vlog.error(
                f"Unexpected error when requesting {self.model.model_name}.\n"
                    + response.text
            )
            Manager.pause(Primitive.WAIT_TIME)
            return self(contents, shorten, retry - 1)

        self.context.append(response_message)
        return response_message
