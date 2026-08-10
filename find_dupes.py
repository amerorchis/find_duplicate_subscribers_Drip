"""Normalize email addresses and find subscribers that share the same real inbox."""

import re
from collections import defaultdict

# Only Gmail treats dots in the local part as insignificant.
DOT_INSENSITIVE_DOMAINS = {'gmail.com', 'googlemail.com'}

EMAIL_PATTERN = re.compile(r'^([^@]+)@([^@]+)$')


def normalize_email(email):
    """Return the canonical form of an email address, or None if unparseable."""
    match = EMAIL_PATTERN.match(email.strip().lower())
    if not match:
        return None
    username, domain = match.groups()

    username = username.split('+', 1)[0]

    if domain in DOT_INSENSITIVE_DOMAINS:
        username = username.replace('.', '')

    return f'{username}@{domain}'


def find_duplicates(emails):
    """Group emails by canonical form and return [(normalized, [variants]), ...]."""
    groups = defaultdict(list)
    skipped = 0
    for email in emails:
        normalized = normalize_email(email)
        if normalized is None:
            print(f'Skipping unparseable email: {email!r}')
            skipped += 1
            continue
        groups[normalized].append(email)

    if skipped:
        print(f'Skipped {skipped} unparseable email(s)')

    return [(normalized, variants) for normalized, variants in sorted(groups.items())
            if len(variants) > 1]
