import sys

from typing import Optional, Dict, Any

sys.dont_write_bytecode = True
from . import TypeSort


# preserved for potential comman kwargs
def spawn_managers() -> Dict[TypeSort, Dict]:
    Sort = TypeSort.Sort

    return {
        TypeSort("ChimeraX", Sort.Raw): {
            "sort": "daily",
            "port": 8000,
            "gui": True,
            "version": "0.5"
        }
    }

def spawn_modules(manager_args: Optional[Dict[TypeSort, Dict]] = None):
    from . import ChimeraX

    frozen = locals()
    if manager_args == None:
        manager_args = spawn_managers()

    return {
        type_sort.type: frozen[type_sort.type]
        for type_sort in manager_args
    }
