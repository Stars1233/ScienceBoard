import sys
import os

from typing import Optional, Dict, Any, TypeAlias

sys.dont_write_bytecode = True
from . import TypeSort
from .base.utils import getitem

# preserved for potential comman kwargs
# all args should have a default value
# should be consisted with Prompts' lambda
Config: TypeAlias = Dict[TypeSort, Dict[str, Any]]
def spawn_managers(vm_path: Optional[str] = None) -> Config:
    Sort = TypeSort.Sort

    return {
        TypeSort.VM: {
            "version": "0.1",
            "vm_path": vm_path,
            "headless": False,
            "port": 8000
        },
        TypeSort.Raw("ChimeraX"): {
            "version": "0.5",
            "sort": "daily",
            "port": 8000,
            "gui": True
        },
        TypeSort.Raw("KAlgebra"): {
            "version": "0.2",
            "bin_path": getitem(os.environ, "KALG_BIN_PATH", None),
            "lib_path": getitem(os.environ, "QT6_LIB_PATH", None),
            "port": 8000
        }
    }

def spawn_modules(manager_args: Optional[Config] = None):
    from . import ChimeraX
    from . import KAlgebra

    frozen = locals()
    if manager_args == None:
        manager_args = spawn_managers()

    return {
        type_sort.type: frozen[type_sort.type]
        for type_sort in manager_args
        if type_sort.sort == TypeSort.Sort.Raw
    }
