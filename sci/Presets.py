import sys

from typing import Optional, Dict, Any, TypeAlias

sys.dont_write_bytecode = True
from . import TypeSort


# preserved for potential comman kwargs
# all args should have a default value
# should be consisted with Prompts' lambda
Config: TypeAlias = Dict[TypeSort, Dict[str, Any]]
def spawn_managers() -> Config:
    Sort = TypeSort.Sort

    return {
        TypeSort("ChimeraX", Sort.Raw): {
            "sort": "daily",
            "port": 8000,
            "gui": True,
            "version": "0.5"
        }
    }

def spawn_modules(manager_args: Optional[Config] = None):
    from . import ChimeraX

    frozen = locals()
    if manager_args == None:
        manager_args = spawn_managers()

    return {
        type_sort.type: frozen[type_sort.type]
        for type_sort in manager_args
    }
