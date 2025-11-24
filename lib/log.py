import logging
from datetime import datetime

file_handler = logging.FileHandler(
    datetime.now().strftime("./logs/%Y-%m-%d_%H-%M-%S.log"), mode="w"
)
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(
    logging.Formatter(
        "%(asctime)s - %(filename)s | %(funcName)s - %(levelname)s - %(message)s"
    )
)

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(filename)s - %(levelname)s - %(message)s")
)

logger = logging.getLogger("lib")
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
