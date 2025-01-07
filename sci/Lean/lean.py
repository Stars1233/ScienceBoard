import sys
import os
import json
import subprocess

from dataclasses import dataclass, asdict
from typing import Dict, List, Union, Optional, Self

sys.dont_write_bytecode
from ..base import Manager


@dataclass
class REPLInput:
    # def __init__(self, *args, **kwargs) -> None:
    #     ...

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
        return json.dumps(asdict(self))


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


# simple encapsulation of Lean REPL
class RawManager(Manager):
    Message = Dict[str, Union[str, int]]
    REPL_URL = "https://github.com/leanprover-community/repl"
    TIMEOUT = 120

    def __init__(
        self,
        version: str,
        lib_path: str = None
    ) -> None:
        super().__init__(version)

        self.lib_path = lib_path
        self.cwd_path = os.path.join(lib_path, "test/Mathlib")
        self.history: List[RawManager.Message] = []

        # None:  proof state not yet entered
        # False: proof not finished
        # True:  proof finished
        self.passed = None

        # download REPL and Mathlib
        if not os.path.exists(os.path.join(lib_path, ".git")):
            assert os.system(f"git clone {RawManager.REPL_URL} {lib_path}") == 0
            assert os.system("lake build repl") == 0
            os.chdir(self.cwd_path)
            assert os.system("lake exe cache get") == 0
            assert os.system("lake build Mathlib") == 0

    def __read(self) -> Dict:
        raw_outputs = ""
        while (line := self.process.stdout.readline()) == "\n": ...
        raw_outputs += line

        while (line := self.process.stdout.readline()) != "\n":
            raw_outputs += line
        return json.loads(raw_outputs)

    def _call(self, query: Message) -> Message:
        output = None

        valid_cmd = ("cmd" in query) \
            and isinstance(query["cmd"], str) \
            and ("env" not in query or type(query["env"]) in (int, type(None))) \
            and len(query) in (1, 2)

        valid_tac = ("tactic" in query) \
            and ("proofState" in query) \
            and isinstance(query["proofState"], int) \
            and len(query) == 2

        if (self.passed is None and valid_cmd) \
            or (self.passed is not None and valid_tac):
            input = json.dumps(query, ensure_ascii=False) + "\n\n"
            self.process.stdin.write(input)
            self.process.stdin.flush()
            output = self.__read()

            if self.passed is None and "sorries" in output:
                assert len(output["sorries"]) == 1
                self.passed = False
                output = {
                    "proofState": output["sorries"][0]["proofState"],
                    "goals": [output["sorries"][0]["goal"]]
                }

            if self.passed is not None \
                and "goals" in output \
                and len(output["goals"]) == 0 \
                and len(output) == 2:
                self.passed = True

        else:
            output = {"message": "Could not parse as a valid JSON command."}

        if self.passed is not None:
            self.history.append(output)
        return output

    def __call__(self, tactic: Message) -> None:
        assert self.passed is not None
        self._call(tactic)

    def __enter__(self) -> Self:
        self.process = subprocess.Popen(
            "lake env ../../.lake/build/bin/repl",
            shell=True,
            cwd=self.cwd_path,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8"
        )

        self.passed = None
        return super().__enter__()

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.process.kill()
        return super().__exit__(exc_type, exc_value, traceback)

    def textual(self) -> str:
        assert len(self.history) > 0
        return json.dumps(self.history[-1], indent=2)
