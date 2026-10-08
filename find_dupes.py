"""Normalize email addresses and find subscribers that share the same real inbox."""

import logging
import re
from collections import defaultdict

from log_utils import mask_email

# Only Gmail treats dots in the local part as insignificant.
DOT_INSENSITIVE_DOMAINS = {"gmail.com", "googlemail.com"}

EMAIL_PATTERN = re.compile(r"^([^@]+)@([^@]+)$")

logger = logging.getLogger(__name__)


def normalize_email(email):
    """Return the canonical form of an email address, or None if unparseable."""
    match = EMAIL_PATTERN.match(email.strip().lower())
    if not match:
        return None
    username, domain = match.groups()

    username = username.split("+", 1)[0]

    if domain in DOT_INSENSITIVE_DOMAINS:
        username = username.replace(".", "")

    return f"{username}@{domain}"


def find_duplicates(emails):
    """Group emails by canonical form and return [(normalized, [variants]), ...]."""
    groups = defaultdict(list)
    skipped = 0
    for email in emails:
        normalized = normalize_email(email)
        if normalized is None:
            logger.warning("Skipping unparseable email: %r", mask_email(email))
            skipped += 1
            continue
        groups[normalized].append(email)

    if skipped:
        logger.info("Skipped %d unparseable email(s)", skipped)

    return [
        (normalized, variants)
        for normalized, variants in sorted(groups.items())
        if len(variants) > 1
    ]
