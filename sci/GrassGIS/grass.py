import sys
import os
import signal
import subprocess

from typing import Dict, Self

import requests
from PIL import Image

sys.dont_write_bytecode = True
from ..base import Manager
from ..vm import VManager


class ManagerMixin:
    STARTUP_WAIT_TIME = 5

    def __init__(self, ip: str, port: int) -> None:
        # legality is not checked due to inner usage
        self.base_url = f"http://{ip}:{port}"

    def status_version(self) -> str:
        return requests.get(self.base_url + "/version").text

    def operate_cmd(self) -> bool:
        return requests.get(self.base_url + "/init/cmd").text == "OK"

    def operate_map(self, grassdb: str, location: str, mapset: str) -> bool:
        return requests.post(self.base_url + "/init/map", json={
            "grassdb": grassdb,
            "location": location,
            "mapset": mapset
        }).text == "OK"

    def operate_layer(self, query: Dict[str, str]) -> bool:
        return requests.post(
            self.base_url + "/init/layer",
            json={"query": query}
        ).text == "OK"

    def operate_scale(self, scale: int) -> bool:
        return requests.post(
            self.base_url + "/init/scale",
            json={"scale": scale}
        ).text == "OK"

    def status_dump(self) -> Dict[str, str]:
        return requests.get(self.base_url + "/dump").json()

    def operate_gcmd(self, cmd: str, kwargs: Dict[str, str]) -> Dict:
        return requests.post(
            self.base_url + "/gcmd",
            json={"cmd": cmd, "kwargs": kwargs}
        ).json()

    def operate_quit(self) -> bool:
        requests.post(self.base_url + "/quit").status_code == 500

class RawManager(Manager, ManagerMixin):
    def __init__(
        self,
        bin_path: str,
        lib_path: str,
        data_path: str,
        version: str = "0.1",
        port: int = 8000
    ) -> None:
        super().__init__(version)

        assert port in range(1024, 65536)
        self.port = port

        # MRO: RawManager -> Manager -> ManagerMixin -> object
        super(Manager, self).__init__("localhost", port)

        assert os.path.isfile(bin_path)
        self.bin_path = bin_path

        assert os.path.isfile(lib_path)
        self.lib_path = lib_path

        assert os.path.isdir(data_path)
        self.data_path = data_path

    def __call__(self, _) -> None:
        raise NotImplementedError

    def __enter__(self) -> Self:
        lock_files = os.path.join(self.data_path, "*/*/.gislock")
        os.system(f"rm -rf {lock_files}")

        self.process = subprocess.Popen((
            f"gnome-terminal "
            f"-- /bin/bash -ic "
            f"\"conda activate grass; "
            f"LD_PRELOAD={self.lib_path} "
            f"FLASK_PORT={self.port} "
            f"/app/bin/grass --gui "
            f"{self.data_path}/world_latlong_wgs84/PERMANENT\"",
        ), shell=True, stdout=subprocess.PIPE, text=True)

        Manager.pause(self.STARTUP_WAIT_TIME)
        assert self.status_version() == self.version
        return super().__enter__()

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.operate_quit()
        super().__exit__(exc_type, exc_value, traceback)

    def screenshot(self) -> Image.Image:
        raise NotImplementedError


class VMManager(VManager, ManagerMixin):
    def __init__(
        self,
        *args,
        port: int = 8000,
        **kwargs
    ) -> None:
        super().__init__(*args, **kwargs)

        assert port in range(1024, 65536)
        self.port = port

    def _post__enter__(self) -> None:
        # MRO: VMManager -> VManager -> Manager -> ManagerMixin -> object
        super(Manager, self).__init__(self.controller.vm_ip, self.port)

    def __enter__(self) -> Self:
        self = super().__enter__()
        self._post__enter__()
        return self
