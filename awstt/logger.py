# -*- coding: utf-8 -*-

import logging
import os


def init_logger():
    if os.getenv("LAMBDA_TASK_ROOT") is None:
        import inspect
        import sys

        from loguru import logger

        class InterceptHandler(logging.Handler):
            def emit(self, record: logging.LogRecord) -> None:
                # Get corresponding Loguru level if it exists.
                level: str | int
                try:
                    level = logger.level(record.levelname).name
                except ValueError:
                    level = record.levelno

                # Find caller from where originated the logged message.
                frame, depth = inspect.currentframe(), 0
                while frame and (depth == 0 or frame.f_code.co_filename == logging.__file__):
                    frame = frame.f_back
                    depth += 1

                logger.opt(depth=depth, exception=record.exc_info).log(level, record.getMessage())

        logger.configure(
            handlers=[
                {
                    "sink": sys.stderr,
                    "format": (
                        "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
                        "<level>{level: <8}</level> | "
                        "<cyan>{name}:{line}</cyan> - <level>{message}</level>"
                    ),
                }
            ]
        )
        logging.getLogger().handlers = [InterceptHandler()]
    else:
        import boto3

        boto3.set_stream_logger("", logging.INFO)

    logging.getLogger().setLevel("INFO")
    logging.getLogger("botocore").setLevel(logging.ERROR)
