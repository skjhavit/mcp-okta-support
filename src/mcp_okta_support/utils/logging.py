"""Structured logging configuration using structlog."""

import logging
import sys
from typing import Any, Dict
import structlog
from rich.console import Console
from rich.logging import RichHandler


def setup_logging(log_level: str = "INFO", structured: bool = True) -> None:
    """Configure structured logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        structured: Whether to use structured logging format
    """
    # Configure standard library logging
    logging.basicConfig(
        level=getattr(logging, log_level),
        handlers=[],  # Remove default handlers
        format="%(message)s",
    )

    if structured:
        # Configure structlog for structured output
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.CallsiteParameterAdder(
                    parameters=[structlog.processors.CallsiteParameter.FUNC_NAME]
                ),
                structlog.dev.ConsoleRenderer(colors=True),
            ],
            wrapper_class=structlog.make_filtering_bound_logger(
                getattr(logging, log_level)
            ),
            logger_factory=structlog.WriteLoggerFactory(),
            cache_logger_on_first_use=True,
        )
    else:
        # Configure rich handler for pretty console output
        console = Console(stderr=True)
        rich_handler = RichHandler(
            console=console,
            show_path=True,
            markup=True,
            rich_tracebacks=True,
        )

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.handlers = [rich_handler]
        root_logger.setLevel(getattr(logging, log_level))

        # Configure structlog to use standard logging
        structlog.configure(
            processors=[
                structlog.contextvars.merge_contextvars,
                structlog.processors.add_log_level,
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
            ],
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a configured logger instance.

    Args:
        name: Logger name (typically __name__)

    Returns:
        Configured structlog logger
    """
    return structlog.get_logger(name)


class RequestContextMiddleware:
    """Middleware to add request context to logs."""

    def __init__(self, request_id: str = None):
        self.request_id = request_id or "unknown"

    def __enter__(self):
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(request_id=self.request_id)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        structlog.contextvars.clear_contextvars()


def log_function_call(logger: structlog.BoundLogger):
    """Decorator to log function calls with parameters and results."""
    def decorator(func):
        async def async_wrapper(*args, **kwargs):
            logger.debug(
                "Function called",
                function=func.__name__,
                args=len(args),
                kwargs=list(kwargs.keys())
            )
            try:
                result = await func(*args, **kwargs)
                logger.debug(
                    "Function completed",
                    function=func.__name__,
                    success=True
                )
                return result
            except Exception as e:
                logger.error(
                    "Function failed",
                    function=func.__name__,
                    error=str(e),
                    error_type=type(e).__name__
                )
                raise

        def sync_wrapper(*args, **kwargs):
            logger.debug(
                "Function called",
                function=func.__name__,
                args=len(args),
                kwargs=list(kwargs.keys())
            )
            try:
                result = func(*args, **kwargs)
                logger.debug(
                    "Function completed",
                    function=func.__name__,
                    success=True
                )
                return result
            except Exception as e:
                logger.error(
                    "Function failed",
                    function=func.__name__,
                    error=str(e),
                    error_type=type(e).__name__
                )
                raise

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper
    return decorator


# Import asyncio at the end to avoid circular imports
import asyncio