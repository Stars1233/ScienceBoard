import primitive
from tactic import Tactics, MetaReturn

import sys
sys.dont_write_bytecode = True


class GeneralTactic(Tactics):
    def __init__(self, theorem: str) -> None:
        super().__init__(theorem)
        self.add_primitives([
            primitive.APPEND,
            primitive.POP
        ])

    def meta_tactic(self) -> MetaReturn:
        getattr(self, "APPEND")("apply Int.natAbs")
        getattr(self, "APPEND")("exact -37")

if __name__ == "__main__":
    tactics = GeneralTactic("def f (x : Unit) : Nat := by sorry")
    print(tactics())
