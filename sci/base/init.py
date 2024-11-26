import sys
import os
import urllib.request
import tempfile

from typing import TYPE_CHECKING

sys.dont_write_bytecode = True
if TYPE_CHECKING:
    from ..vm.vmanager import VManager


def raw_download(url, path) -> bool:
    path = os.path.expanduser(path)
    urllib.request.urlretrieve(url, path)
    return True

def vm_download(url, path, manager: "VManager") -> bool:
    path = os.path.expanduser(path)
    _, filename = os.path.split(path)
    temp_path = os.path.join(manager.temp_dir, filename)
    urllib.request.urlretrieve(url, temp_path)
    return manager._vmrun("CopyFileFromHostToGuest", temp_path, path)[1]
