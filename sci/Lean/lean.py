import sys
import os
import json
import subprocess

from typing import Dict, List, Union, Self

sys.dont_write_bytecode
from ..base import Manager
from .format import *


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
        # self.passed = None

        # download REPL and Mathlib
        if not os.path.exists(os.path.join(lib_path, ".git")):
            self.__fetch()

    def __fetch(self) -> None:
        assert os.system(f"git clone {RawManager.REPL_URL} {self.lib_path}") == 0
        assert os.system("lake build repl") == 0

        os.chdir(self.cwd_path)
        assert os.system("lake exe cache get") == 0
        assert os.system("lake build Mathlib") == 0

    def __read(self) -> Dict:
        raw_outputs = ""
        read_line = lambda: self.process.stdout.readline()

        while (line := read_line()) == "\n": ...
        raw_outputs += line

        while (line := read_line()) != "\n":
            raw_outputs += line
        return json.loads(raw_outputs)

    def _call(self, query: Message, tactic_only: bool = False) -> REPLOutput:
        input = REPLInput.from_dict(query)
        output = None

        if isinstance(input, REPLInputTactic) \
            or (not tactic_only and isinstance(input, REPLInputCommand)):
            self.process.stdin.write(input.dump())
            self.process.stdin.flush()
            output = REPLOutput.from_dict(self.__read())

            # if self.passed is None and "sorries" in output:
            #     assert len(output["sorries"]) == 1
            #     self.passed = False
            #     output = {
            #         "proofState": output["sorries"][0]["proofState"],
            #         "goals": [output["sorries"][0]["goal"]]
            #     }

            # if self.passed is not None \
            #     and "goals" in output \
            #     and len(output["goals"]) == 0 \
            #     and len(output) == 2:
            #     self.passed = True

        else:
            output = REPLOutput(
                message="Could not parse as a valid JSON tactic."
            )

        # if self.passed is not None:
        #     self.history.append(output)
        output.input = input
        return output

    def __call__(self, tactic: str) -> None:
        self._call(json.loads(tactic), tactic_only=True)

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
