import base64
import dataclasses

from dataclasses import dataclass, asdict
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

# ---

@dataclass
class Content:
    type: Literal["text", "image"]
    text: Optional[str] = None
    image: Optional[Image.Image] = None

    def _openai_text(self) -> Dict[str, Any]:
        return {
            "type": "text",
            "text": self.text
        }

    def _openai_image(self) -> Dict[str, Any]:
        self.image.save(buffered:=BytesIO(), format="PNG")
        image_base64 = base64.b64encode(buffered.getvalue())

        return {
            "type": "image_url",
            "image_url": {
                "url": f"data:image/png;base64, {image_base64.decode()}",
                "detail": "high"
            }
        }

    def _anthropic_text(self) -> Dict[str, Any]:
        return {
            "type": "text",
            "text": self.text
        }

    def _anthropic_image(self) -> Dict[str, Any]:
        raise NotImplementedError

    def _asdict(self, style: str) -> Dict[str, Any]:
        func_name = f"_{style}_{self.type}"
        assert hasattr(self, func_name)
        return getattr(self, func_name)()




print(
    asdict(Message(style="openai", role="user", content=[
        Content(type="text", text="haha"),
        Content(type="text", text="xixi")
    ]))
)

# TODO: model.message
