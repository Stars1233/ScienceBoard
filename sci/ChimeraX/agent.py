import sys

sys.dont_write_bytecode = True
from ..agent import Agent, Content
from ..task import Task

class ChimeraXAgent(Agent):
    def _init_system_message(self):
        super()._init_system_message("You are a helpful assistant...")

    def __call__(self, task: Task) -> None:
        contents = [Content(
            type="text",
            text="Who won the world series in 2020?"
        )]
        response_message = super().__call__(contents)
        print(response_message.content[0].text)

        task.manager.run("style ball")
