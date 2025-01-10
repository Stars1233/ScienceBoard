import sys
import os

from typing import Optional, Dict, Any
from typing import Callable, TypeAlias

sys.dont_write_bytecode = True
from . import TypeSort

# preserved for potential comman kwargs
# all args should have a default value
# should be consisted with Prompts' lambda
# add lambda function for lazy loading
Config: TypeAlias = Dict[TypeSort, Callable[[], Dict[str, Any]]]
def spawn_managers(vm_path: Optional[str] = None) -> Config:
    return {
        TypeSort.VM: lambda: {
            "version": "0.1",
            "vm_path": vm_path,
            "headless": False,
            "port": 8000
        },
        TypeSort.Raw("ChimeraX"): lambda: {
            "version": "0.5",
            "sort": "daily",
            "port": 8000,
            "gui": True
        },
        TypeSort.Raw("KAlgebra"): lambda: {
            "version": "0.3",
            "bin_path": os.environ["KALG_BIN_PATH"],
            "lib_path": os.environ["QT6_LIB_PATH"],
            "port": 8000
        },
        TypeSort.Raw("Lean"): lambda: {
            "version": "0.1",
            "lib_path": os.environ["LEAN_LIB_PATH"],
        }
    }

def spawn_modules(manager_args: Optional[Config] = None):
    from . import ChimeraX
    from . import KAlgebra
    from . import Lean

    frozen = locals()
    if manager_args == None:
        manager_args = spawn_managers()

    return {
        type_sort.type: frozen[type_sort.type]
        for type_sort in manager_args
        if type_sort.sort == TypeSort.Sort.Raw
    }
