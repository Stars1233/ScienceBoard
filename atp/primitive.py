from typing import Set, Callable

import sys
sys.dont_write_bytecode = True
PRIMITIVES: Set[Callable] = set()
INDEX_ASSERT: str = "index out of range"


def APPEND(self, tactic: str) -> None:
    self.tactics.append(tactic)

def POP(self) -> None:
    if len(self.tactics) < 1:
        return
    del self.tactics[-1]

def MOD(self, index: int, tactic: str) -> None:
    assert 0 <= index and index < len(self.tactics), INDEX_ASSERT
    self.tactics[index] = tactic

def INSERT(self, index: int, tactic) -> None:
    assert 0 <= index and index <= len(self.tactics), INDEX_ASSERT
    self.tactics.insert(index, tactic)

def DELETE(self, index: int) -> None:
    assert 0 <= index and index < len(self.tactics), INDEX_ASSERT
    del self.tactics[index]


if len(PRIMITIVES) == 0:
    this_vars = list(vars())
    for entity_name in this_vars:
        entity = sys.modules[__name__].__dict__[entity_name]
        if hasattr(entity, "__call__") \
            and entity.__module__ in ["__main__", "primitive"]:
            PRIMITIVES.add(entity)
