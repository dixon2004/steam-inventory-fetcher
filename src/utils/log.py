import logging.handlers
import logging
import os


if not os.path.exists("./logs"):
    os.makedirs("./logs")


def setup_logger(name: str, log_file: str, log_level: int, backup_count: int = 7) -> logging.Logger:
    """
    Setup logger for the bot.

    Args:
        name (str): Name of the logger.
        log_file (str): Path to the log file.
        log_level (int): Log level.
        backup_count (int): Number of backup logs to keep.

    Returns:
        logging.Logger: Logger object.
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    formatter = logging.Formatter(fmt='%(asctime)s - %(levelname)s - %(message)s')

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.handlers.TimedRotatingFileHandler(log_file, when='D', backupCount=backup_count)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger_info = setup_logger("infoLog", "./logs/info.log", logging.INFO)
logger_error = setup_logger("errorLog", "./logs/error.log", logging.ERROR)


def write_log(log_type: str, message: str) -> None:
    """
    Write log message to the log file.

    Args:
        log_type (str): Type of the log message.
        message (str): Log message. 
    """
    try:
        if log_type == "debug":
            logger_info.debug(message)
        elif log_type == "info":
            logger_info.info(message)
        elif log_type == "warning":
            logger_error.warning(message)
        elif log_type == "error":
            logger_error.error(message)
        elif log_type == "critical":
            logger_error.critical(message)
        else:
            logger_error.error("[Logging] Unknown log method")
    except Exception as e:
        logger_error.error(f"[Logging] Failed to write log message: {e}")
