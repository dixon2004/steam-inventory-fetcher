import logging.handlers
import logging
import queue
import os


class SyncLogger:

    _listener: logging.handlers.QueueListener | None = None
    _queue: queue.Queue = queue.Queue(-1)
    _all_handlers: list[logging.Handler] = []

    def __init__(
        self,
        class_name: str,
        log_level: str = "INFO",
        log_path: str = "../logs",
        backup_count: int = 3,
        max_bytes: int = 100 * 1024 * 1024,
    ) -> None:
        """
        Initializes the SyncLogger for the given class with rotating file and console handlers.

        Args:
            class_name (str): Name of the class or module owning this logger.
            log_level (str, optional): Logging level (e.g., "DEBUG", "INFO"). Defaults to "INFO".
            log_path (str, optional): Directory to store log files. Defaults to "../logs".
            backup_count (int, optional): Number of backup log files to retain. Defaults to 3.
            max_bytes (int, optional): Maximum log file size in bytes before rotation. Defaults to 100 MB.
        """
        self.class_name = class_name
        self.log_path = log_path
        self.backup_count = backup_count
        self.max_bytes = max_bytes

        os.makedirs(self.log_path, exist_ok=True)

        log_level_int = getattr(logging, log_level.upper(), logging.INFO)

        self.formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        self.logger_info = self._setup_logger("infoLog", "info.log", log_level_int)
        self.logger_error = self._setup_logger("errorLog", "error.log", logging.ERROR)

        self._log_map = {
            "debug": self.logger_info.debug,
            "info": self.logger_info.info,
            "warning": self.logger_error.warning,
            "error": self.logger_error.error,
            "critical": self.logger_error.critical,
        }

        self._start_listener()


    def _setup_logger(self, name: str, log_file: str, log_level: int) -> logging.Logger:
        """
        Sets up a logger with the specified name, log file, and log level.

        Args:
            name (str): The name of the logger.
            log_file (str): The name of the log file where logs will be written.
            log_level (int): The logging level for the logger.

        Returns:
            logging.Logger: The configured logger instance.
        """
        logger = logging.getLogger(name)

        if logger.hasHandlers():
            if logger.level == logging.NOTSET or log_level < logger.level:
                logger.setLevel(log_level)
            return logger

        logger.setLevel(log_level)

        if not any(isinstance(h, logging.StreamHandler) and not isinstance(h, logging.FileHandler) for h in SyncLogger._all_handlers):
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(self.formatter)
            SyncLogger._all_handlers.append(console_handler)

        file_path = os.path.join(self.log_path, log_file)
        file_handler = logging.handlers.RotatingFileHandler(
            file_path, maxBytes=self.max_bytes, backupCount=self.backup_count
        )
        file_handler.setFormatter(self.formatter)
        file_handler.setLevel(log_level)
        SyncLogger._all_handlers.append(file_handler)

        queue_handler = logging.handlers.QueueHandler(SyncLogger._queue)
        logger.addHandler(queue_handler)

        logger.propagate = False
        return logger


    def _start_listener(self) -> None:
        """
        Starts the queue listener if it hasn't been started already, dispatching records to all registered handlers.
        """
        if SyncLogger._listener is None:
            SyncLogger._listener = logging.handlers.QueueListener(
                SyncLogger._queue, *SyncLogger._all_handlers, respect_handler_level=True
            )
            SyncLogger._listener.start()


    def write_log(self, log_type: str, message: str, exc: Exception | None = None) -> None:
        """
        Writes a log message of the specified type, optionally including exception information.

        Args:
            log_type (str): The type of log message (e.g., "debug", "info", "warning", "error", "critical").
            message (str): The log message to be written.
            exc (Exception | None, optional): An optional exception to include in the log message. Defaults to None.
        """
        log_func = self._log_map.get(log_type.lower())

        if log_func:
            msg = f"[{self.class_name}] {message}"
            if exc:
                log_func(msg, exc_info=exc)
            else:
                log_func(msg)
        else:
            self.logger_error.error(f"[{self.class_name}] Unknown log type: {log_type}")
