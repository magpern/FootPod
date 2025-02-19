import logging
import os
from config import LOG_LEVEL

# Create logs directory if not exists
if not os.path.exists("logs"):
    os.makedirs("logs")

# Configure logging
LOG_FILE = "logs/app.log"

logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),  # Use config value, default to INFO
    format="%(asctime)s [%(levelname)s] [%(module)s] %(message)s",
    handlers=[
        logging.FileHandler(LOG_FILE, mode="w", encoding="utf-8"),
        logging.StreamHandler()
    ],
)

logger = logging.getLogger(__name__)
