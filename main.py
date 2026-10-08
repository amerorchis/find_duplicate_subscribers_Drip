"""Find duplicate Drip subscribers and email the report to the configured recipients."""

import logging
import os
import sys
from datetime import datetime

from drip import retrieve_emails
from find_dupes import find_duplicates
from log_utils import configure_logging
from save_excel import save_excel
from send_email import email_spreadsheet

REQUIRED_ENV_VARS = [
    "DRIP_TOKEN",
    "DRIP_ACCOUNT",
    "FROM_ALERT_EMAIL",
    "FROM_ALERT_PWD",
    "RECIPS",
]

logger = logging.getLogger(__name__)


def main():
    """Set up logging and run the pipeline, exiting non-zero on any failure."""
    configure_logging()
    try:
        run()
    except Exception:
        logger.exception("Duplicate subscriber report failed")
        sys.exit(1)


def run():
    """Run the full pipeline: fetch, find duplicates, save spreadsheet, email it."""
    missing = [var for var in REQUIRED_ENV_VARS if not os.environ.get(var)]
    if missing:
        logger.error("Missing required environment variables: %s", ", ".join(missing))
        sys.exit(1)

    recipients = [r.strip() for r in os.environ["RECIPS"].split(",") if r.strip()]

    email_list = retrieve_emails()
    results = find_duplicates(email_list)
    logger.info("Found %d duplicate group(s)", len(results))

    os.makedirs("files", exist_ok=True)
    spreadsheet_name = f"files/duplicate_emails_{datetime.now().astimezone().strftime('%-m_%-d_%y')}.xlsx"
    save_excel(results, spreadsheet_name)

    if os.environ.get("DRY_RUN"):
        logger.info(
            "DRY_RUN set: skipping email send. Would have sent %s to %d recipient(s)",
            spreadsheet_name,
            len(recipients),
        )
    else:
        email_spreadsheet(spreadsheet_name, recipients)


if __name__ == "__main__":
    main()
