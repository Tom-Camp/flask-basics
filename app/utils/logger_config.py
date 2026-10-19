"""
Copyright 2019-2026 CivicActions, Inc. See the README file at the top-level
directory of this distribution and at https://github.com/CivicActions/flask-basics#license.
"""

import logging
import os

from logging.config import dictConfig

from flask import g, has_request_context

from app.utils.helpers import BASE_DIR

LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()


class RequestIdFilter(logging.Filter):
    def filter(self, record):
        record.request_id = g.get("request_id", "-") if has_request_context() else "-"
        return True


dictConfig(
    {
        "version": 1,
        "disable_existing_loggers": False,
        "filters": {"request_id": {"()": RequestIdFilter}},
        "formatters": {
            "default": {
                "format": "%(asctime)s | %(levelname)-8s | %(request_id)s | %(name)s:%(lineno)d - %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "filters": ["request_id"],
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "filename": (LOG_DIR / "app.log").as_posix(),
                "maxBytes": 10_000_000,
                "backupCount": 5,
                "formatter": "default",
                "filters": ["request_id"],
            },
        },
        "root": {"level": LOG_LEVEL, "handlers": ["console", "file"]},
    }
)
