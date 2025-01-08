import json

from typing import List, Optional
from dataclasses import dataclass, asdict

@dataclass
class REPLInput:
    @staticmethod
    def from_dict(query: dict) -> Optional["REPLInput"]:
        if ("cmd" in query) \
            and isinstance(query["cmd"], str) \
            and ("env" not in query or type(query["env"]) in (int, type(None))) \
            and len(query) in (1, 2):
            return REPLInputCommand(**query)

        elif ("tactic" in query) \
            and ("proofState" in query) \
            and isinstance(query["tactic"], str) \
            and isinstance(query["proofState"], int) \
            and len(query) == 2:
            return REPLInputTactic(**query)

        else:
            return None

    def dump(self) -> str:
        return json.dumps(asdict(self)) + "\n\n"


@dataclass
class REPLInputCommand(REPLInput):
    cmd: str
    env: Optional[int] = None


@dataclass
class REPLInputTactic(REPLInput):
    tactic: str
    proofState: int


@dataclass
class REPLOutput:
    input: Optional[REPLInput] = None
    message: Optional[str] = None
    messages: Optional[List] = None

    @staticmethod
    def from_dict(output: dict) -> "REPLOutput":
        return REPLOutputCommand(**output) \
            if "env" in output \
            else REPLOutputTactic(**output)

    def from_sorry(sorry: dict) -> "REPLOutputTactic":
        return REPLOutputTactic(
            proofState=sorry["proofState"],
            goals=[sorry["goal"]]
        )

    def is_error(self) -> bool:
        return self.message is not None \
            or any([item["severity"] == "error" for item in self.messages])


@dataclass
class REPLOutputCommand(REPLOutput):
    env: int = -1
    sorries: Optional[List] = None


@dataclass
class REPLOutputTactic(REPLOutput):
    proofState: Optional[int] = None
    goals: Optional[List] = None

    def is_success(self) -> bool:
        return not self.is_error() \
            and isinstance(self.goals, list) \
            and len(self.goals) == 0
