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

from typing import List, Dict, Tuple, Optional, Callable

sys.dont_write_bytecode
from .. import Manager

# raw: supposed that ChimeraX is pre-installed on Linux
#      and one of commands in SORT_MAP is runnable
class ChimeraXManagerRaw(Manager):
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
    TIMEOUT = 10
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
        super().__init__()

        assert sort in ChimeraXManagerRaw.SORT_MAP
        self.sort = sort

        assert port in range(1024, 65536)
        self.port = port

        assert isinstance(gui, bool)
        self.gui = gui

        assert re.match(r'^\d+\.\d+$', version) is not None
        self.version = version

        self.__temp_dir = tempfile.TemporaryDirectory()
        self.temp_dir = self.__temp_dir.name

    def __del__(self) -> None:
        self.__temp_dir.cleanup()

    def __call(self, command: str) -> Dict:
        return requests.get(
            ChimeraXManagerRaw.BASE_URL(self.port),
            params={"command": command}
        ).json()

    def _call(self, command: str) -> Tuple[List[str], bool]:
        response = self.__call(command)
        return (
            response["log messages"]["note"],
            response["error"] is None
        )

    def __call__(self, command: str) -> None:
        self.__call(command)

    def states_dump(self) -> dict:
        timestamp = str(int(time.time() * 1000))
        self(f"states {self.temp_dir} {timestamp}")
        return json.load(open(
            os.path.join(self.temp_dir, timestamp + ".json"),
            mode="r",
            encoding="utf-8"
        ))

    def destroy_cli(self) -> bool:
        assert float(self.version) >= 0.3
        _, code = self._call("destroy")
        return code

    def clear_history(self) -> bool:
        assert float(self.version) >= 0.4
        _, code = self._call("clear")
        return code

    def __check_version(self) -> Optional[str]:
        version_pattern = r'[.\d]+'
        target_pattern = fr'SessionStates(\*\*)? \({version_pattern}\)'

        log_message, _ = self._call("toolshed list")
        bundle_list = log_message[1].split("\n")
        target_matched = [
            re.search(version_pattern, item)[0]
            for item in bundle_list
            if re.search(target_pattern, item)
        ]

        if len(target_matched) > 0:
            return target_matched[0]
        else:
            return None

    def __install_bundle(self, version: str, uninstall: bool = True) -> None:
        zip_file_path = os.path.join(self.temp_dir, f"{version}.zip")
        bundle_dir_path = os.path.join(self.temp_dir, f"chimerax-states-{version}")
        urllib.request.urlretrieve(ChimeraXManagerRaw.TOOL_URL(version), zip_file_path)

        with zipfile.ZipFile(zip_file_path, "r") as zip_ref:
            zip_ref.extractall(self.temp_dir)

        if uninstall:
            self("toolshed uninstall SessionStates")
        self(f"devel install {bundle_dir_path}")

    def __prepare_env(self, desired_version: str) -> None:
        current_version = self.__check_version()
        if current_version != desired_version:
            self.__install_bundle(desired_version, current_version is not None)

    def __enter__(self) -> "ChimeraXManagerRaw":
        nogui = [] if self.gui else ["--nogui"]
        self.process = subprocess.Popen([
            *ChimeraXManagerRaw.SORT_MAP[self.sort],
            *nogui,
            "--cmd",
            f"remotecontrol rest start json true port {self.port}",
        ], stdout=subprocess.PIPE, text=True)

        timeout = time.time() + ChimeraXManagerRaw.TIMEOUT
        while True:
            if self.process.stdout.readline().startswith(ChimeraXManagerRaw.REST_FLAG):
                self.__prepare_env(self.version)
                self.entered = True
                return self
            assert time.time() <= timeout, "Timeout when opening ChimeraX"

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.process.kill()
        self.entered = False

    # TODO
    def screenshot(self) -> str:
        return ""
