import sys

sys.dont_write_bytecode = True
from .. import Agent, Content, Message
from .. import Task

class ChimeraXAgent(Agent):
    def _init_system_message(self) -> None:
        super()._init_system_message("""
You are an agent which follow my instruction and perform desktop computer tasks as instructed, and you are required to use ChimeraX Command Line Interface to perform the action.

You ONLY need to return the code inside a code block, like this:
```
# your code here
```
When you think the task is done, just return ```DONE```.

You are asked to complete the following task: Change the display of atoms to ball and stick style in ChimeraX.
""")

    def __extract_antiquot(self, response_message: Message) -> str:
        import re
        response_text = response_message.content[0].text
        match = re.search(r'```(?:\w+\s+)?([\w\W]*?)```', response_text)
        return match[1].strip() if match is not None else ""

    def __call__(self, task: Task) -> None:
        for step_index in range(self.max_steps):
            inst = "What's the next step that you will do to help with the task?"
            response_message = super().__call__([Content.text_content(inst)])
            response_code = self.__extract_antiquot(response_message)
            if response_code == "DONE":
                break
            task.manager.run(response_code)
