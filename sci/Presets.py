import sys

from typing import Optional, Dict

sys.dont_write_bytecode = True
from . import Manager, Model, Agent
from . import Prompts

from . import ChimeraX

def spawn_agents(
    model_style: str,
    base_url: str,
    model_name: str,
    api_key: Optional[str] = None,
    proxy: Optional[str] = None,
    access_style: str = "openai",
    code_style: str = "antiquot",
    overflow_style: Optional[str] = None,
) -> Dict[str, Agent]:
    model = Model(
        style=model_style,
        base_url=base_url,
        model_name=model_name,
        api_key=api_key,
        proxy=proxy
    )

    return {
        "ChimeraX:Raw": Agent(
            model=model,
            access_style=access_style,
            code_style=code_style,
            overflow_style=overflow_style,
            system_inst=Prompts.SYSTEM_INST_CHIMERAX_RAW
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
