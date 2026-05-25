import logging
import os


#create logs if directory does'nt create it
os.makedirs("logs", exist_ok=True)


#configure loggger
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



logger = logging.getLogger("IntelliRetailAI")