import sys
import os
import re
import time
import json
import zipfile
import requests
import subprocess
import tempfile
import urllib.request

from typing import List, Dict, Optional, Callable

sys.dont_write_bytecode = True
from task import Task

class ChimeraX:
    SORT_MAP: Dict[str, List[str]] = {
        "stable": [
            "chimerax"
        ],
        "daily": [
            "chimerax-daily"
        ],
        "flatpak": [
            "flatpak",
            "run",
            "edu.ucsf.rbvi.ChimeraX"
        ]
    }
    REST_FLAG: str = "REST server started"
    BASE_URL: Callable[[int], str] = lambda port: f"http://localhost:{port}/run"
    TOOL_URL: Callable[[str], str] = lambda version: \
        f"https://github.com/ShiinaHiiragi/chimerax-states/archive/refs/tags/{version}.zip"

    def __init__(
        self,
        sort: str = "stable",
        port: int = 8000,
        gui: bool = False,
        version: str = "0.2"
    ) -> None:
        assert sort in ChimeraX.SORT_MAP
        self.sort = sort

        assert port in range(1024, 65536)
        self.port = port

        assert isinstance(gui, bool)
        self.gui = gui

        assert re.match(r'^\d+\.\d+$', version) is not None
        self.version = version

        self.entered = False
        self.__temp_dir = tempfile.TemporaryDirectory()
        self.temp_dir = self.__temp_dir.name

    def __del__(self) -> None:
        self.__temp_dir.cleanup()

    def __run(self, command: str) -> Dict:
        return requests.get(
            ChimeraX.BASE_URL(self.port),
            params={"command": command}
        ).json()

    def _run(self, command: str) -> bool:
        response = self.__run(command)
        return response["error"] is None

    def run(self, command: str) -> List[str]:
        return self.__run(command)["log messages"]["note"]

    def __check_version(self) -> Optional[str]:
        version_pattern = r'[.\d]+'
        target_pattern = fr'SessionStates(\*\*)? \({version_pattern}\)'

        bundle_list = self.run("toolshed list")[1].split("\n")
        target_matched = [
            re.search(version_pattern, item)[0]
            for item in bundle_list
            if re.search(target_pattern, item)
        ]

        if len(target_matched) > 0:
            return target_matched[0]
        else:
            return None

    def __install_bundle(self, version: str, uninstall=True) -> None:
        zip_file_path = os.path.join(self.temp_dir, f"{version}.zip")
        bundle_dir_path = os.path.join(self.temp_dir, f"chimerax-states-{version}")
        urllib.request.urlretrieve(ChimeraX.TOOL_URL(version), zip_file_path)
        
        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall(self.temp_dir)

        if uninstall:
            self.run("toolshed uninstall SessionStates")
        self.run(f"devel install {bundle_dir_path}")

    def __prepare_env(self, desired_version: str) -> None:
        current_version = self.__check_version()
        if current_version != desired_version:
            self.__install_bundle(desired_version, current_version is not None)

    def __enter__(self) -> "ChimeraX":
        nogui = [] if self.gui else ["--nogui"]
        self.process = subprocess.Popen([
            *ChimeraX.SORT_MAP[self.sort],
            *nogui,
            "--cmd",
            f"remotecontrol rest start json true port {self.port}",
        ], stdout=subprocess.PIPE, text=True)

        while True:
            if self.process.stdout.readline().startswith(ChimeraX.REST_FLAG):
                self.__prepare_env(self.version)
                self.entered = True
                return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.process.kill()
        self.entered = False

    def states_dump(self) -> dict:
        timestamp = str(int(time.time() * 1000))
        self.run(f"states {self.temp_dir} {timestamp}")
        return json.load(open(
            os.path.join(self.temp_dir, timestamp + ".json"),
            mode="r",
            encoding="utf-8"
        ))

    def destroy_cli(self) -> bool:
        assert float(self.version) >= 0.3
        return self._run("destroy")

    def clear_history(self) -> bool:
        assert float(self.version) >= 0.4
        return self._run("clear")


class ChimeraXTask(Task):
    AgentType = ChimeraX

    def __init__(self, config_path: str, manager: ChimeraX) -> None:
        super().__init__(config_path)

        assert isinstance(manager, ChimeraX)
        self.manager = manager
        self.__check_config()

    def __check_config(self) -> None:
        assert "version" in self.config
        self.version = self.config["version"]
        assert isinstance(self.version, str)
        assert self.version == self.manager.version

        for init_item in self.initialize:
            assert "func" in init_item
            assert isinstance(init_item["func"], str)

        for eval_item in self.evaluate:
            for key_name in eval_item:
                assert key_name in ("find", "key", "value")
                assert isinstance(eval_item[key_name], str)

    def __recover(self) -> bool:
        return self.manager._run("close") and self.manager.clear_history()

    def __open(self, name: str) -> bool:
        return self.manager._run(f"open {name}")

    def __exec(self, cmd: str) -> bool:
        return self.manager._run(cmd)

    def exec_init(self) -> bool:
        init = lambda func, **kwargs: getattr(self, f"_ChimeraXTask__{func}")(**kwargs)
        for round_index in range(Task.CONFIG_RETRY):
            self.__recover()
            success_list = [init(**init_item) for init_item in self.initialize]
            if all(success_list):
                return True
        return False

    @Task._error_handler
    def __eval_states(self, current_states, eval_item):
        find = eval_item["find"] if "find" in eval_item else None
        key = eval_item["key"]
        value = eval_item["value"]

        raw_key = None
        if key.startswith("lambda"):
            key = eval(key)

        # find meta_key by key-value pair using find(key)
        # process meta_key to raw_key using key(meta_key)
        # type of find: (str, Any) -> bool
        # type of key: str -> str
        if find is not None:
            find = eval(find)
            meta_keys = list(filter(find, current_states.items()))
            raw_key = key(meta_keys[0][0])

        # find raw_key directly using key(key)
        # type of key: str -> bool
        elif hasattr(key, "__call__"):
            raw_keys = list(filter(key, current_states.keys()))
            raw_key = raw_keys[0]

        # key itself is raw_key
        # type of key: str
        else:
            raw_key = key

        # get targeted raw_value by raw_key
        raw_value = current_states[raw_key]
        if not isinstance(raw_value, str):
            raw_value = json.dumps(raw_value)
        return re.search(value, raw_value) is not None

    def exec_eval(self) -> bool:
        current_states = self.manager.states_dump()
        for eval_item in self.evaluate:
            if not self.__eval_states(current_states, eval_item):
                return False
        return True
