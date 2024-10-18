from typing import Any, Self

# abstract base class of all apps, subclass should include
# - __call__(): execute code, no feedback expected
# - __enter__() / __exit__(): open / close app
# - entered: whether app is opened
class Manager:
    def __init__(self) -> None:
        self.entered = False

    def __call__(self) -> None:
        raise NotImplementedError

    def __enter__(self) -> Self:
        self.entered = True
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.entered = False
