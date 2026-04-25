import logging
# TODO: usee datetime
from datetime import datetime, timezone


def get_logger(name: str = __name__):
    """Return a simple logger with UTC datetime and log level information."""
    logger = logging.getLogger(name)
    if not logger.hasHandlers():
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        formatter.converter = lambda *args: datetime.fromtimestamp(args[0], tz=timezone.utc).timetuple()
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger