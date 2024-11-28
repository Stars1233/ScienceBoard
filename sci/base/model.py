import base64
import requests

import dataclasses
from dataclasses import dataclass
from requests import Response
from io import BytesIO

from typing import Optional, List, Dict
from typing import Literal, Any, Self

from PIL import Image

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
class Content:
    def _asdict(self, style: str = "openai") -> Dict[str, Any]:
        return getattr(self, f"_{style}")()

    def __dict_factory_override__(self) -> Dict[str, Any]:
        return self._asdict()


@dataclass
class TextContent(Content):
    text: str

    def __asdict(self) -> Dict[str, Any]:
        return {
            "type": "text",
            "text": self.text
        }

    def _openai(self) -> Dict[str, Any]:
        return self.__asdict()

    def _anthropic(self) -> Dict[str, Any]:
        return self.__asdict()


@dataclass
class ImageContent(Content):
    image: Image.Image

    def _openai(self) -> Dict[str, Any]:
        self.image.save(buffered:=BytesIO(), format="PNG")
        image_base64 = base64.b64encode(buffered.getvalue())

        return {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64, {image_base64.decode()}",
                "detail": "high"
            }
        }

    # TODO
    def _anthropic(self) -> Dict[str, Any]:
        raise NotImplementedError


@dataclass
class Message:
    # message's style follows model_style
    style: Literal["openai", "anthropic"]
    role: Literal["system", "user", "assistant"]
    content: List[Content]

    def _asdict(self, context: Optional[int] = None) -> Dict[str, Any]:
        result = {
            "role": self.role,
            "content": [
                content._asdict(self.style)
                for content in self.content
            ]
        }

        if context is not None:
            result["context_length"] = context
        return result

    def __dict_factory_override__(self) -> Dict[str, Any]:
        return self._asdict()


@dataclass
class Model:
    model_style: str
    base_url: str
    model_name: str
    api_key: Optional[str] = None
    proxy: Optional[str] = None
    version: Optional[str] = None
    max_tokens: int = 1500
    top_p: float = 0.9
    temperature: float = 0.5

    def message(
        self,
        role: Literal["system", "user", "assistant"],
        content: List[Content] = []
    ) -> Message:
        return Message(style=self.model_style, role=role, content=content)

    @property
    def proxies(self) -> Dict:
        return None if self.proxy is None else {
            "http": self.proxy,
            "https": self.proxy
        }

    def _style_openai(self, messages: Dict) -> Response:
        headers = {
            "Content-Type": "application/json",
        }

        if self.api_key is not None:
            headers["Authorization"] = f"Bearer {self.api_key}"

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
            proxies=self.proxies,
            json=payload
        )

    def _style_anthropic(self, messages: Dict) -> Response:
        assert self.api_key is not None
        assert self.version is not None
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": self.version,
            "content-type": "application/json"
        }

        payload = {
            "model": self.model,
            "max_tokens": self.max_tokens,
            "messages": messages,
            "temperature": self.temperature,
            "top_p": self.top_p
        }

        return requests.post(
            self.base_url,
            headers=headers,
            proxies=self.proxies,
            json=payload
        )

    def __call__(self, messages: Dict) -> Response:
        return getattr(self, f"_style_{self.model_style}")(messages)

    @staticmethod
    def _access_openai(response: Response) -> Message:
        message = response.json()["choices"][0]["message"]
        return Message(
            style="openai",
            role=message["role"],
            content=[TextContent(message["content"])]
        )

    # TODO
    @staticmethod
    def _access_anthropic(response: Response) -> Message:
        raise NotImplementedError

    def access(self, response: Response) -> Message:
        return getattr(Model, f"_access_{self.model_style}")(response)
