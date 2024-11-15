import sys
from typing import Dict, Callable

sys.dont_write_bytecode = True
from . import Manager, Model, Agent
from . import Prompts

from . import ChimeraX

AGENT_KEYS = [
    "ChimeraX:Raw"
]

def instruct_handler(spawner: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        result_dict: Dict[str, Agent] = spawner(*args, **kwargs)
        for key, value in result_dict.items():
            code_prompt = value.code_style
            type_sort = key.replace(":", "_")
            prompt_name = f"{code_prompt}_{type_sort}".upper()
            value.system_inst = getattr(Prompts, prompt_name)
        return result_dict
    return wrapper

@instruct_handler
def spawn_agents(**kwargs) -> Dict[str, Agent]:
    model_kwargs = {
        key: value for key, value in kwargs.items()
        if key in Model.__dataclass_fields__.keys()
    }

    agent_kwargs = {
        key: value for key, value in kwargs.items()
        if key not in Model.__dataclass_fields__.keys()
    }

    model = Model(**model_kwargs)
    return {key: Agent(model=model, **agent_kwargs) for key in AGENT_KEYS}

def spawn_managers() -> Dict[str, Manager]:
    return{
        "ChimeraX:Raw": ChimeraX.RawManager(
            sort="daily",
            port=8000,
            gui=True,
            version="0.5"
        )
    }
