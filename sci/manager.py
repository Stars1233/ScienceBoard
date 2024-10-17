from typing import Self

# abstract base class
# 
class Manager:
    def __init__(self) -> None:
        self.entered = False

    def __enter__(self) -> Self:
        self.entered = True
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.entered = False
