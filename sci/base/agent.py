import re
import requests

from enum import Enum
from dataclasses import dataclass, asdict
from requests import Response

from typing import Optional, List, Dict, Callable, Literal, Any, Self
from typing import TYPE_CHECKING

if TYPE_CHECKING: from .task import Task

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
    def image_content(url: str) -> Self:
        return Content(
            type="image_url",
            image_url={"url": url, "detail": "high"}
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
        call_func = getattr(self, f"_Model__style_{self.style}")
        return call_func(messages)


class Access:
    @staticmethod
    def openai(response: Response) -> Message:
        message = response.json()["choices"][0]["message"]
        return Message(
            role=message["role"],
            content=[Content.text_content(message["content"])]
        )


class Overflow:
    @staticmethod
    def openai_gpt(response: Response) -> bool:
        return response.status_code != 200 \
            and response.json()["error"]["code"] == "context_length_exceeded"

    @staticmethod
    def openai_lmdeploy(response: Response) -> bool:
        return Access.openai(response).content == ""


@dataclass
class CodeLike:
    code: str
    class PRIMITIVE(Enum):
        DONE = 1
        FAIL = 0
        WAIT = -1
        EXEC = -2

    @staticmethod
    def extract_antiquot(content: Content) -> Self:
        match_obj = re.search(r'```(?:\w+\s+)?([\w\W]*?)```', content.text)
        code = match_obj[1].strip() if match_obj is not None else ""
        return CodeLike(code=code)

    def __call__(self, task: "Task") -> None:
        if not self.code in CodeLike.PRIMITIVE._member_names_:
            task.manager(self.code)


# base class for all agents, subclass should include
# - _init_system_message(): fill system prompts by super()._init_system_message()
# - __call__(): policy of agents; call llm by super().__call__()
class Agent:
    def __init__(
        self,
        model: Model,
        access_handler: Callable[[Response], Message] = Access.openai,
        code_handler: Callable[[Content], CodeLike] = CodeLike.extract_antiquot,
        overflow_handler: Optional[Callable[[Response], bool]] = None,
        context_window_size: int = 3
    ) -> None:
        assert isinstance(model, Model)
        self.model = model

        assert hasattr(access_handler, "__call__")
        self.access_handler = access_handler

        assert hasattr(code_handler, "__call__")
        self.code_handler = code_handler

        assert overflow_handler is None or hasattr(overflow_handler, "__call__")
        self.overflow_handler = overflow_handler

        assert isinstance(context_window_size, int)
        self.context_window_size = context_window_size

        self._init_system_message()
        self.context_window: List[Message] = []

    def _init_system_message(
        self,
        text: str = "You are a helpful assistant."
    ) -> None:
        self.system_message: Message = Message(
            role="system",
            content=[Content.text_content(text)]
        )

    def _step_user_contents(self, task) -> List[Content]:
        inst = "What's the next step that you will do to help with the task?"
        return [Content.text_content(inst)]

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

        is_overflow = False if self.overflow_handler is None \
            else self.overflow_handler(response)

        if is_overflow and not shorten:
            return self(contents, shorten)
        assert not is_overflow, f"Tokens overflow when calling {self.model.model_name}"

        response_message = self.access_handler(response)
        self.context_window.append(response_message)
        return response_message
