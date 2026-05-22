import logging
import os


# create logs directory if not exists
os.makedirs("logs", exist_ok=True)


# configure logger
logging.basicConfig(
    level=logging.INFO,

    format=(
        "%(asctime)s | "
        "%(levelname)s | "
        "%(name)s | "
        "%(message)s"
    ),

    handlers=[
        logging.FileHandler("logs/app.log"),
        logging.StreamHandler()
    ]
)


# create logger instance
logger = logging.getLogger("IntelliRetailAI")