import os

class Log:
    def __init__(self, log_path: str) -> None:
        os.makedirs(log_path, exist_ok=True)
        self.path = log_path
