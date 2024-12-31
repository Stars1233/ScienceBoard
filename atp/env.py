import json
import subprocess
import pathlib
from typing import List, Dict, Iterable, Optional, Union

import sys
sys.dont_write_bytecode = True
InputType = Dict[str, Union[str, int]]
OutputType = List[Dict]


class REPL:
    CMD = "lake env ../../.lake/build/bin/repl"
    CWD = "C:/Users/Ichinoe/Repository/temp/repl/test/Mathlib"
    TMP = ".temp"
    CKPT = "base.olean"

    def __init__(self) -> None:
        self.cwd_path = pathlib.Path(REPL.CWD)
        self.inputs: List[InputType] = []
        assert self.cwd_path.exists()

        self.temp_path = pathlib.Path(*self.cwd_path.parts[:-2], REPL.TMP)
        self.ckpt_path = self.temp_path / REPL.CKPT
        if not self.temp_path.exists():
            self.temp_path.mkdir()

        if not self.ckpt_path.exists():
            self.run_init()

    def run_init(self) -> OutputType:
        self.clear()
        self.add_cmd("import Mathlib\nopen BigOperators Real Nat Topology")
        self.pickle_env(self.ckpt_path, env=0)
        return self.run()

    def run_tactics(
        self,
        theorem: str,
        tactics: Iterable[str] = []
    ) -> OutputType:
        self.clear()
        self.unpickle_env(self.ckpt_path)
        self.add_cmd(theorem, env=0)
        for index, tactic in enumerate(tactics):
            self.add_tactic(tactic, proof_state=index)
        return self.run()

    def clear(self) -> None:
        self.inputs.clear()

    def add_cmd(self, cmd: str, env: Optional[int] = None) -> None:
        raw_input: Dict[str, Union[str, int]] = { "cmd": cmd }
        if env != None:
            assert env >= 0
            raw_input["env"] = env
        self.inputs.append(raw_input)

    def add_tactic(self, tactic: str, proof_state: int) -> None:
        assert proof_state >= 0
        self.inputs.append({
            "tactic": tactic,
            "proofState": proof_state
        })

    def pickle_env(self, path: Union[str, pathlib.Path], env: int) -> None:
        if isinstance(path, pathlib.Path):
            path = str(path)
        assert env >= 0
        self.inputs.append({
            "pickleTo": path,
            "env": env
        })

    def unpickle_env(self, path: Union[str, pathlib.Path]) -> None:
        if isinstance(path, pathlib.Path):
            path = str(path)
        assert pathlib.Path(path).exists()
        self.inputs.append({
            "unpickleEnvFrom": path
        })

    def run(self, inputs: Optional[List[InputType]] = None) -> OutputType:
        proc: subprocess.Popen = subprocess.Popen(
            REPL.CMD,
            cwd=REPL.CWD,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            encoding="utf-8"
        )

        raw_input: str = "\n\n".join(map(
            lambda item: json.dumps(
                item,
                ensure_ascii=False
            ),
            self.inputs if inputs == None else inputs
        ))

        raw_output, _ = proc.communicate(
            input=raw_input,
            timeout=120
        )

        self.inputs.clear()
        return list(map(
            lambda item: json.loads(item),
            raw_output.split("\n\n")[:-1]
        ))
