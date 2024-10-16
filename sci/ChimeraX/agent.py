import sys
from typing import List

sys.dont_write_bytecode = True
from ..agent import Agent, Content, Message

class ChimeraXAgent(Agent):
    def __call__(self, contents: List[Content]) -> Message:
        return super().__call__(contents)
