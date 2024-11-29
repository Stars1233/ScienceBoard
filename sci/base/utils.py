from enum import Enum
from typing import Optional, Dict, Any
from typing import Callable, ClassVar, Self
from dataclasses import dataclass

class SortVM():
    def __get__(self, _, objtype=None) -> Optional["TypeSort"]:
        if hasattr(globals(), "TypeSort"):
            return TypeSort("", TypeSort.Sort.VM)


@dataclass
class TypeSort:
    class Sort(Enum):
        Raw = 0
        VM = 1

    type: str
    sort: Sort

    VM: ClassVar[Optional[Self]] = SortVM()

    def __repr__(self) -> str:
        if self.sort == TypeSort.Sort.VM:
            return self.sort.name
        else:
            return f"{self.sort.name}:{self.type}"

    def __hash__(self) -> int:
        return hash(self.__repr__())

    # crucial for hash comparison
    def __eq__(self, __value: "TypeSort") -> bool:
        return self.__repr__() == __value.__repr__()

    def __str__(self) -> str:
        return f"{self.type}_{self.sort.name}"

    def __call__(self, postfix: str) -> Any:
        return self.sort.name + postfix


def error_factory(default_value):
    def error_handler(method: Callable) -> Callable:
        def error_wrapper(self, *args, **kwargs) -> bool:
            try:
                return method(self, *args, **kwargs)
            except:
                return default_value
        return error_wrapper
    return error_handler

def getitem(obj: Dict, name: str, default: Any) -> Any:
    return obj[name] if name in obj else default
