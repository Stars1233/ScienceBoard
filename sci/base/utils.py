import inspect

from enum import Enum
from typing import Optional, Dict, Any
from typing import Callable, ClassVar, Self
from dataclasses import dataclass

class SortVM():
    def __get__(self, _, obj_type=None) -> Optional["TypeSort"]:
        if inspect.signature(obj_type).parameters.__len__():
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

RawType = lambda type: TypeSort(type, TypeSort.Sort.Raw)
VMType = lambda type: TypeSort(type, TypeSort.Sort.Raw)


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
