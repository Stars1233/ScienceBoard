import os
import urllib.request

def raw_download(url, path) -> bool:
    path = os.path.expanduser(path)
    urllib.request.urlretrieve(url, path)
    return True
