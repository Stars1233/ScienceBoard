import requests

from dataclasses import dataclass
from typing import Any, Optional, List, Dict, Callable

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

    def __style_openai(self, messages: Dict) -> requests.Response:
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
    def __style_anthropic(self, messages: Dict) -> requests.Response:
        ...

    def __call__(self, messages: Dict) -> requests.Response:
        call_func = getattr(self, f"_Model__style_{self.style}")
        return call_func(messages)


class Agent:
    def __init__(
        self,
        model: Model,
        overflow_handler: Optional[Callable] = None,
        context_window_size: int = 3
    ) -> None:
        assert isinstance(model, Model)
        self.model = model

        assert overflow_handler is None or hasattr(overflow_handler, "__call__")
        self.overflow_handler = overflow_handler

        assert isinstance(context_window_size, int)
        self.context_window_size = context_window_size

        self.history_messages: List = []

    def __call__(self) -> Dict:
        ...


class Overflow:
    @staticmethod
    def gpt(response: requests.Response) -> bool:
        return response.status_code != 200 \
            and response.json()["error"]["code"] == "context_length_exceeded"

    @staticmethod
    def lmdeploy(response: requests.Response) -> bool:
        return response.json()["choices"][0]["message"]["content"] == ""


if __name__ == "__main__":
    model = Model(
        style="openai",
        base_url="http://server.ichinoe.xyz:500/v1/chat/completions",
        model_name="/mnt/workspace/ichinoe/model/InternVL2-8B/snapshots/357996b2cba121dce8748498968e9fddcc62e386",
    )

    response = model(messages=[
        {
            "role": "system",
            "content": "You are a helpful assistant."
        },
        {
            "role": "user",
            "content": "Who won the world series in 2020?"
        },
        {
            "role": "assistant",
            "content": "The Los Angeles Dodgers won the World Series in 2020."
        },
        {
            "role": "user",
            "content": "Where was it played?"
        }
    ])

    import json
    print(response.status_code)
    print(json.dumps(response.json(), indent=2))
