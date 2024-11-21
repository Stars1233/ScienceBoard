import sys

from typing import Optional, Dict, Any, TypeAlias

sys.dont_write_bytecode = True
from . import TypeSort


# preserved for potential comman kwargs
# all args should have a default value
# should be consisted with Prompts' lambda
Config: TypeAlias = Dict[TypeSort, Dict[str, Any]]
def spawn_managers(vm_path: Optional[str] = None) -> Config:
    Sort = TypeSort.Sort

    return {
        TypeSort("", Sort.VM): {
            "version": "0.1",
            "vm_path": vm_path,
            "headless": False
        },
        TypeSort("ChimeraX", Sort.Raw): {
            "version": "0.5",
            "sort": "daily",
            "port": 8000,
            "gui": True
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
        if len(type_sort.type) > 0
    }
