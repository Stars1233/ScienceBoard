import sys

sys.dont_write_bytecode = True
from ..agent import Agent, Content

class ChimeraXAgent(Agent):
    def _load_system_message(self):
        super()._load_system_message("You are a helpful assistant...")

    def __call__(self) -> str:
        contents = [Content(
            type="text",
            text="Who won the world series in 2020?"
        )]
        response_message = super().__call__(contents)
        response_text = response_message.content[0].text
        return response_text
