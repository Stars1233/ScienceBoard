import sys

from typing import Optional, Dict, Callable

sys.dont_write_bytecode = True
from . import Manager, Model, Agent
from . import Prompts

from . import ChimeraX

def load_system_inst(spawner: Callable) -> Callable:
    def wrapper(*args, **kwargs):
        result_dict: Dict[str, Agent] = spawner(*args, **kwargs)
        for key, value in result_dict.items():
            code_prompt = value.code_style.upper()
            type_sort = key.replace(":", "_").upper()
            value.system_inst = getattr(Prompts, f"{code_prompt}_{type_sort}")
        return result_dict
    return wrapper

@load_system_inst
def spawn_agents(
    model_style: str,
    base_url: str,
    model_name: str,
    api_key: Optional[str] = None,
    proxy: Optional[str] = None,
    max_tokens: int = 1500,
    top_p: float = 0.9,
    temperature: float = 0.5,
    access_style: str = "openai",
    code_style: str = "antiquot",
    overflow_style: Optional[str] = None,
    context_window: int = 3
) -> Dict[str, Agent]:
    model = Model(
        style=model_style,
        base_url=base_url,
        model_name=model_name,
        api_key=api_key,
        proxy=proxy,
        max_tokens=max_tokens,
        top_p=top_p,
        temperature=temperature
    )

    return {
        "ChimeraX:Raw": Agent(
            model=model,
            access_style=access_style,
            code_style=code_style,
            overflow_style=overflow_style,
            context_window=context_window
        )
    }

def spawn_managers() -> Dict[str, Manager]:
    return{
        "ChimeraX:Raw": ChimeraX.RawManager(
            sort="daily",
            port=8000,
            gui=True,
            version="0.4"
        )
    }
