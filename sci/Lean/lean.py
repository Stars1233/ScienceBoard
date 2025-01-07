import sys
import os
import json
import subprocess

from typing import Dict, List, Union, Self

sys.dont_write_bytecode
from ..base import Manager

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
        self.history: RawManager.Message = {}
        self.passed = False

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

    def __call__(self, tactic: Message) -> None:
        valid_cmd = ("cmd" in tactic) \
            and isinstance(tactic["cmd"], str) \
            and ("env" not in tactic or isinstance(tactic["env"], int))

        valid_tac = ("tactic" in tactic) \
            and ("proofState" in tactic) \
            and isinstance(tactic["proofState"], int)

        if valid_cmd or valid_tac:
            input = json.dumps(tactic, ensure_ascii=False) + "\n\n"
            self.process.stdin.write(input)
            self.process.stdin.flush()

            self.history = self.__read()
            if len(self.history["goals"]) == 0:
                self.passed = True

        else:
            self.history = {
                "message": "Could not parse as a valid JSON command."
            }

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

        self.passed = False
        return super().__enter__()

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.process.kill()
        return super().__exit__(exc_type, exc_value, traceback)

    def textual(self) -> str:
        return json.dumps(self.history, indent=2)
