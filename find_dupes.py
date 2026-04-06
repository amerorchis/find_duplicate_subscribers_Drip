import re
from collections import defaultdict
from itertools import combinations


def normalize_email(email):
    email_pattern = r'^([^@]+)@([^@]+)$'
    match = re.match(email_pattern, email)
    if not match:
        raise ValueError(f"Invalid email format: {email}")
    username, domain = match.groups()

    if domain not in ['outlook.com', 'hotmail.com', 'yahoo.com']:
        username = username.replace('.', '')

    username = re.sub(r'\+.*', '', username)

    return username + '@' + domain


def find_duplicates(emails):
    groups = defaultdict(list)
    for email in emails:
        groups[normalize_email(email)].append(email)

    duplicates = []
    for group in groups.values():
        if len(group) > 1:
            duplicates.extend(combinations(group, 2))

    return duplicates
