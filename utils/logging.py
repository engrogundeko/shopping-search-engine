import logging
import colorlog
import os
from logging.handlers import RotatingFileHandler

# Ensure logs directory exists
LOG_DIR = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(LOG_DIR, exist_ok=True)

# Set up the logger
logger = logging.getLogger("custom_logger")
logger.setLevel(logging.DEBUG)  # Set the default log level to DEBUG

# Define a colored formatter for console
console_formatter = colorlog.ColoredFormatter(
    "%(asctime)s - %(log_color)s%(levelname)s%(reset)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    log_colors={
        "DEBUG": "cyan",
        "INFO": "green",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "bold_red",
    },
)

# Define a standard formatter for file logging
file_formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

# Create console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(console_formatter)

# Create rotating file handler for all logs
log_file_path = os.path.join(LOG_DIR, 'application.log')
file_handler = RotatingFileHandler(
    log_file_path, 
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=5  # Keep 5 backup files
)
file_handler.setLevel(logging.INFO)  # Log INFO and above to file
file_handler.setFormatter(file_formatter)

# Create error file handler
error_log_file_path = os.path.join(LOG_DIR, 'error.log')
error_file_handler = RotatingFileHandler(
    error_log_file_path, 
    maxBytes=10*1024*1024,  # 10 MB
    backupCount=3  # Keep 3 backup files
)
error_file_handler.setLevel(logging.ERROR)  # Only log ERROR and CRITICAL
error_file_handler.setFormatter(file_formatter)

# Add handlers to the logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)
logger.addHandler(error_file_handler)

# Prevent log messages from propagating to parent loggers
logger.propagate = False