from enum import Enum
from typing import List, Dict, Iterable, Callable, Optional, NoReturn
from env import REPL, OutputType

import sys
sys.dont_write_bytecode = True
MetaReturn = Optional[NoReturn]


class Proof:
    class State(Enum):
        PASS = "PASS"
        NORMAL = "NORMAL"
        ERROR = "ERROR"

    def __init__(self) -> None:
        self.repl: REPL = REPL()

    def verify_theorem(self, theorem: str) -> None:
        output = self.repl.run_tactics(theorem)
        assert len(output) == 2
        assert "sorries" in output[-1]
        assert len(output[-1]["sorries"]) == 1

    def verify(self, theorem: str, tactics: List[str]) -> Dict:
        output = self.repl.run_tactics(theorem, tactics)
        return Proof.check_tactic(output)

    @staticmethod
    def check_tactic(output: OutputType) -> Dict:
        assert len(output) > 2
        for sub_index, item in enumerate(output[2:]):
            if "message" in item:
                return {
                    "state": Proof.State.ERROR,
                    "index": sub_index,
                    "message": item["message"]
                }

            if "messages" in item:
                filtered = filter(
                    lambda msg: msg["severity"] == "error",
                    item["messages"]
                )
                casted = list(map(
                    lambda msg: msg["data"],
                    filtered
                ))

                if len(casted) > 0:
                    return {
                        "state": Proof.State.ERROR,
                        "index": sub_index,
                        "messages": casted
                    }

            continue

        if len(output[-1]["goals"]) == 0:
            return {
                "state": Proof.State.PASS
            }
        else:
            return {
                "state": Proof.State.NORMAL,
                "goals": output[-1]["goals"]
            }


class Tactics:
    INDEX_ASSERT: str = "index out of range"

    def __init__(self, theorem: str) -> None:
        self.proof: Proof = Proof()
        self.tactics: List[str] = []

        self.theorem: str = theorem
        self.proof.verify_theorem(self.theorem)
        self.verify = self.proof.verify

    def add_primitives(self, func_iter: Iterable[Callable]) -> None:
        for func in func_iter:
            self.__setattr__(func.__name__, func.__get__(self))

    def meta_tactic(self) -> MetaReturn:
        raise NotImplementedError

    def __call__(self) -> Proof.State:
        self.tactics.clear()
        self.meta_tactic()
        return self.proof.verify(self.theorem, self.tactics)["state"]
