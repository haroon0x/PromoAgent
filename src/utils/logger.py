import sys
from loguru import logger

# Remove default handler to avoid duplicate logs
logger.remove()

# Configure console logger with a nice format and colors
logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan> - <level>{message}</level>",
    colorize=True,
)

# Configure file logger
# This will create a new log file when the current one reaches 10 MB
# It will keep the logs for 10 days and compress old ones
logger.add(
    "log/promoagent_{time}.log",
    level="DEBUG",
    rotation="10 MB",
    retention="10 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    enqueue=True,  # Make it process-safe
    backtrace=True,
    diagnose=True,
)

# Export the configured logger
__all__ = ["logger"] 