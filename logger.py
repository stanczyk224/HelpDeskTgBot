import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler


LOG_DIR = Path("Logs")
LOG_DIR.mkdir(exist_ok=True)


file_handler = RotatingFileHandler(
    filename=LOG_DIR / "bot.log",
    maxBytes=5 * 1024 * 1024,  # 5 MB
    backupCount=3,
    encoding="utf-8",
    delay=True,
)
file_handler.setLevel(logging.DEBUG)


error_handler = RotatingFileHandler(
    filename=LOG_DIR / "errors.log",
    maxBytes=2 * 1024 * 1024,  # 2 MB
    backupCount=3,
    encoding="utf-8",
    delay=True,
)
error_handler.setLevel(logging.ERROR)


stream_handler = logging.StreamHandler(stream=sys.stdout)
stream_handler.setLevel(logging.INFO)


logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        stream_handler,
        file_handler,
        error_handler,
    ],
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)