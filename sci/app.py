# abstract base class
class Application:
    def __init__(self) -> None:
        self.entered = False

    def __enter__(self) -> "Application":
        self.entered = True
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.entered = False
