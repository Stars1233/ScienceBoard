from enum import Enum

class Test:
    def __enter__(self):
        print("ENTER")
        return self

    def __exit__(self, _, __, ___):
        print("EXIT")

test = Test()
with test as test:
    test.__exit__(None, None, None)
    test.__enter__()

class PRIMITIVE:
    @staticmethod
    def DONE():
        raise

    @staticmethod
    def FAIL():
        raise

    @staticmethod
    def WAIT():
        raise

getattr(PRIMITIVE, "DONE")()
