from typing import Dict, Any

def getitem(obj: Dict, name: str, default: Any) -> Any:
    return obj[name] if name in obj else default
