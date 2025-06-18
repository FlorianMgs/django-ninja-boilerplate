import logging
from channels.db import database_sync_to_async


# Create a WebSocket-safe logger that only uses console handlers
def get_websocket_logger():
    """Get a logger that only uses console handlers (no database logging)"""
    logger = logging.getLogger("websocket")
    if not logger.handlers:
        # Only add console handler, no database handler
        console_handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "{levelname} {asctime} {module} {process:d} {thread:d} {message}", style="{"
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
        logger.setLevel(logging.INFO)
        logger.propagate = False  # Don't propagate to parent loggers
    return logger


# WebSocket-safe logger instance
websocket_logger = get_websocket_logger()


@database_sync_to_async
def log_info_to_db(message):
    """Async-safe function to log info messages to database"""
    db_logger = logging.getLogger("db")
    db_logger.info(message)


@database_sync_to_async
def log_error_to_db(message):
    """Async-safe function to log error messages to database"""
    db_logger = logging.getLogger("db")
    db_logger.error(message)


@database_sync_to_async
def log_exception_to_db(message, exc_info=True):
    """Async-safe function to log exceptions to database"""
    db_logger = logging.getLogger("db")
    db_logger.exception(message, exc_info=exc_info)


@database_sync_to_async
def log_warning_to_db(message):
    """Async-safe function to log warning messages to database"""
    db_logger = logging.getLogger("db")
    db_logger.warning(message)


# Convenience functions that log to console immediately and database asynchronously
async def async_log_info(message):
    """Log info message to console immediately and database asynchronously"""
    websocket_logger.info(message)
    await log_info_to_db(message)


async def async_log_error(message):
    """Log error message to console immediately and database asynchronously"""
    websocket_logger.error(message)
    await log_error_to_db(message)


async def async_log_exception(message, exc_info=True):
    """Log exception to console immediately and database asynchronously"""
    websocket_logger.exception(message, exc_info=exc_info)
    await log_exception_to_db(message, exc_info=exc_info)


async def async_log_warning(message):
    """Log warning message to console immediately and database asynchronously"""
    websocket_logger.warning(message)
    await log_warning_to_db(message)
