# # server/app/utils/logging.py

# import logging

# def setup_logging():
#     logging.basicConfig(level=logging.DEBUG)  # Adjust the logging level here

# # server/app/utils/logging.py
# import logging
# import sys

# # Define ANSI escape codes for colors
# class LogColors:
#     RESET = "\033[0m"
#     RED = "\033[91m"
#     GREEN = "\033[92m"
#     YELLOW = "\033[93m"
#     BLUE = "\033[94m"

# # Custom Formatter to handle colors
# class ColoredFormatter(logging.Formatter):
#     def format(self, record):
#         if record.levelno == logging.ERROR:
#             record.msg = f"{LogColors.RED}{record.msg}{LogColors.RESET}"
#         elif record.levelno == logging.INFO:
#             record.msg = f"{LogColors.GREEN}{record.msg}{LogColors.RESET}"
#         elif record.levelno == logging.WARNING:
#             record.msg = f"{LogColors.YELLOW}{record.msg}{LogColors.RESET}"
#         elif record.levelno == logging.DEBUG:
#             record.msg = f"{LogColors.BLUE}{record.msg}{LogColors.RESET}"
#         return super().format(record)

# def setup_logging():
#     # Create logger
#     logger = logging.getLogger()

#     # Set logging level (adjustable)
#     logger.setLevel(logging.DEBUG)  # You can change this to INFO, ERROR, etc.

#     # Create console handler with color formatter
#     handler = logging.StreamHandler(sys.stdout)
#     formatter = ColoredFormatter("%(asctime)s - %(levelname)s - %(message)s")
#     handler.setFormatter(formatter)

#     # Add the handler to the logger
#     if not logger.hasHandlers():
#         logger.addHandler(handler)

#     return logger

import logging
import sys

# Define ANSI escape codes for colors
class LogColors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"

# Custom Formatter to handle colors
class ColoredFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.ERROR:
            record.msg = f"{LogColors.RED}{record.msg}{LogColors.RESET}"
        elif record.levelno == logging.INFO:
            record.msg = f"{LogColors.GREEN}{record.msg}{LogColors.RESET}"
        elif record.levelno == logging.WARNING:
            record.msg = f"{LogColors.YELLOW}{record.msg}{LogColors.RESET}"
        elif record.levelno == logging.DEBUG:
            record.msg = f"{LogColors.BLUE}{record.msg}{LogColors.RESET}"
        return super().format(record)

def setup_logging():
    # Create logger
    logger = logging.getLogger()

    # Set logging level (adjustable)
    logger.setLevel(logging.DEBUG)  # You can change this to INFO, ERROR, etc.

    # Create console handler with color formatter
    handler = logging.StreamHandler(sys.stdout)
    formatter = ColoredFormatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)

    # Add the handler to the logger
    if not logger.hasHandlers():
        logger.addHandler(handler)

    return logger
