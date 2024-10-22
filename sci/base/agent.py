import sys
import re
import time
import base64
import requests

from dataclasses import dataclass, asdict
from requests import Response
from io import BytesIO

from typing import Optional, List, Dict, Set
from typing import Callable, Literal, Any, Self
from PIL import Image

sys.dont_write_bytecode = True
from .manager import Manager
from .log import VirtualLog

# modify asdict() for class Content
# ref: https://stackoverflow.com/a/78289335
import dataclasses
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
class Content:
    type: Literal["text", "image_url"]
    text: Optional[str] = None
    image_url: Optional[Dict[str, str]] = None

    @staticmethod
    def text_content(text: str) -> Self:
        return Content(type="text", text=text)

    @staticmethod
    def image_content(image: Image.Image) -> Self:
        image.save(buffered:=BytesIO(), format="JPEG")
        image_base64 = base64.b64encode(buffered.getvalue())

        return Content(
            type="image_url",
            image_url={
                "url": f"data:image/png;base64, {image_base64.decode()}",
                "detail": "high"
            }
        )

    def __dict_factory_override__(self) -> dict[str, Any]:
        return {
            key: getattr(self, key)
            for key in self.__dataclass_fields__
            if getattr(self, key) is not None
        }


@dataclass
class Message:
    role: Literal["system", "user", "assistant"]
    content: List[Content]


@dataclass
class Model:
    style: str
    base_url: str
    model_name: str
    api_key: Optional[str] = None
    proxy: Optional[str] = None
    max_tokens: int = 1500
    top_p: float = 0.9
    temperature: float = 0.5

    def __style_openai(self, messages: Dict) -> Response:
        headers = {
            "Content-Type": "application/json",
        }

        if self.api_key is not None:
            headers["Authorization"] = f"Bearer {self.api_key}"

        proxies = None if self.proxy is None else {
            "http": self.proxy,
            "https": self.proxy
        }

        payload = {
            "model": self.model_name,
            "messages": messages,
            "max_tokens": self.max_tokens,
            "top_p": self.top_p,
            "temperature": self.temperature
        }

        return requests.post(
            self.base_url,
            headers=headers,
            proxies=proxies,
            json=payload
        )

    # TODO
    def __style_anthropic(self, messages: Dict) -> Response:
        ...

    def __call__(self, messages: Dict) -> Response:
        full_name = f"_{self.__class__.__name__}__style_{self.style}"
        return getattr(self, full_name)(messages)


class Access:
    @staticmethod
    def openai(response: Response) -> Message:
        message = response.json()["choices"][0]["message"]
        return Message(
            role=message["role"],
            content=[Content.text_content(message["content"])]
        )


class Primitive:
    class PlannedTermination(Exception):
        def __init__(self, type: staticmethod) -> None:
            self.type = type

    @staticmethod
    def DONE():
        raise Primitive.PlannedTermination(Primitive.DONE)

    @staticmethod
    def FAIL():
        raise Primitive.PlannedTermination(Primitive.FAIL)

    @staticmethod
    def WAIT():
        time.sleep(Agent.WAIT_TIME)

    @staticmethod
    def TIMEOUT():
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
    def PRIMITIVE(self):
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
        return Access.openai(response).content == ""


class Agent:
    WAIT_TIME = 5

    SYSTEM_INST = lambda inst: f"You are asked to complete the following task: {inst}"
    USER_FLATTERY = "What's the next step that you will do to help with the task?"
    USER_OPENING: Dict[Set[str], str] = {
        frozenset({
            Manager.screenshot.__name__
        }): "Given the screenshot as below. ",
        frozenset({
            Manager.a11y_tree.__name__
        }): "Given the info from accessibility tree as below:\n{a11y_tree}\n",
        frozenset({
            Manager.set_of_marks.__name__
        }): "Given the tagged screenshot as below. ",
        frozenset({
            Manager.screenshot.__name__,
            Manager.a11y_tree.__name__
        }): "Given the screenshot and info from accessibility tree as below:\n{a11y_tree}\n"
    }

    def __init__(
        self,
        model: Model,
        access_style: str = "openai",
        code_style: str = "antiquot",
        overflow_style: Optional[str] = None,
        system_inst: Optional[Callable[[str], str]] = None,
        context_window_size: int = 3
    ) -> None:
        assert isinstance(model, Model)
        self.model = model

        assert hasattr(Access, access_style)
        self.access_handler: Callable[
            [Response],
            Message
        ] = getattr(Access, access_style)

        assert hasattr(CodeLike, f"extract_{code_style}")
        self.code_handler: Callable[
            [Content],
            List[CodeLike]
        ] = getattr(CodeLike, f"extract_{code_style}")

        assert overflow_style is None or hasattr(Overflow, overflow_style)
        self.overflow_handler: Optional[Callable[[Response], bool]] = None \
            if overflow_style is None \
            else getattr(Overflow, overflow_style)

        if system_inst is None:
            system_inst = Agent.SYSTEM_INST
        assert hasattr(system_inst, "__call__")
        self.SYSTEM_INST: Callable[[str], str] = system_inst
        self.init()

        assert isinstance(context_window_size, int)
        self.context_window_size = context_window_size
        self.context_window: List[Message] = []

        self.vlog = VirtualLog()

    def init(self, inst: str) -> None:
        self.system_message: Message = Message(
            role="system",
            content=[Content.text_content(self.SYSTEM_INST)]
        )

    def step(self, obs: Dict[str, Any]) -> List[Content]:
        a11y_tree = obs[Manager.a11y_tree.__name__] \
            if Manager.a11y_tree.__name__ in obs else None
        opening = self.USER_OPENING[frozenset(obs.keys())].format(a11y_tree=a11y_tree)
        contents = [Content.text_content(opening + Agent.USER_FLATTERY)]

        images = [item for _, item in obs.items() if isinstance(item, Image.Image)]
        contents += [Content.image_content(image) for image in images]
        return contents

    def __dump(self, context_count: int) -> Dict:
        return [asdict(message) for message in [
            self.system_message,
            *self.context_window[-context_count:]
        ]]

    def dump_payload(self) -> Dict:
        return self.__dump(self.context_window_size * 2 + 1)

    def dump_history(self) -> Dict:
        return self.__dump(len(self.context_window))

    def __call__(
        self,
        contents: List[Content],
        shorten: bool = False
    ) -> Message:
        assert isinstance(contents, list)
        for content in contents:
            assert isinstance(content, Content)

        self.context_window.append(Message(role="user", content=contents))
        response = self.model(messages=self.dump_payload())

        if response.status_code != 200:
            self.vlog.warning(f"Getting response code of {response.status_code}")

        is_overflow = False if self.overflow_handler is None \
            else self.overflow_handler(response)

        if is_overflow and not shorten:
            return self(contents, shorten)
        assert not is_overflow, f"Tokens overflow when calling {self.model.model_name}"

        response_message = self.access_handler(response)
        self.context_window.append(response_message)
        return response_message
