import sys

from typing import List

sys.dont_write_bytecode = True
from .. import Agent, Content
from .. import Task

class ChimeraXAgent(Agent):
    def _init_system_message(self) -> None:
        self.DEFAULT_SYSTEM_PROMPT = """
You are an agent which follow my instruction and perform desktop computer tasks as instructed, and you are required to use ChimeraX Command Line Interface to perform the action.

You ONLY need to return the code inside a code block, like this:
```
# your code here
```
When you think the task is done, just return ```DONE```.

You are asked to complete the following task: Change the display of atoms to ball and stick style in ChimeraX.
"""

        super()._init_system_message()
