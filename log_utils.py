"""Logging setup and helpers shared by the pipeline."""

import logging
import sys

LOG_FORMAT = "%(asctime)s - %(levelname)s - %(message)s"
LOG_DATEFMT = "%Y-%m-%d %H:%M:%S"


def configure_logging():
    """Send timestamped, levelled lines to stderr; cron appends them to cron.log."""
    logging.basicConfig(
        level=logging.INFO, format=LOG_FORMAT, datefmt=LOG_DATEFMT, stream=sys.stderr
    )


def mask_email(email):
    """Hide all but the first character of an address's local part, e.g. 'j***@gmail.com'."""
    email = email.strip()
    local, at, domain = email.rpartition("@")
    if not at:
        local, domain = email, ""
    return f"{local[:1]}***{at}{domain}"
