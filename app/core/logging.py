import logging
import os

def setup_logging():
    os.makedirs("logs", exist_ok=True)  # 🧩 <-- создаёт папку, если её нет

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("logs/warehouse.log"),
            logging.StreamHandler()
        ]
    )