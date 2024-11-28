from enum import Enum
from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class TypeSort:
    class Sort(Enum):
        Raw = 0
        VM = 1

    type: str
    sort: Sort

    def __str__(self) -> str:
        return f"{self.type}_{self.sort.name}"

    def __repr__(self) -> str:
        if self.sort == TypeSort.Sort.VM:
            return self.sort.name
        else:
            return f"{self.sort.name}:{self.type}"

    def __call__(self, postfix: str) -> Any:
        return self.sort.name + postfix

    # crucial for hash comparison
    def __eq__(self, __value: "TypeSort") -> bool:
        return self.__repr__() == __value.__repr__()

    def __hash__(self) -> int:
        return hash(self.__repr__())


def getitem(obj: Dict, name: str, default: Any) -> Any:
    return obj[name] if name in obj else default
