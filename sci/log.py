import os
import logging

class Log:
    def __init__(self) -> None:
        ...

    def switch(log_path: str):
        log_path = os.path.expanduser(log_path)
        os.makedirs(log_path, exist_ok=True)

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(fmt=(
        "\x1b[1;33m[%(asctime)s "
        "\x1b[31m%(levelname)s "
        "\x1b[32m%(module)s/%(lineno)d-%(processName)s"
        "\x1b[1;33m] "
        "\x1b[0m%(message)s"
    ))

    stream_handler = logging.StreamHandler()
    stream_handler.setLevel(logging.DEBUG)
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    logger.info("TEST")
