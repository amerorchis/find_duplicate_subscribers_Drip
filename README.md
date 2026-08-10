# find_duplicate_subscribers_Drip

Generate a report of emails that are recognized as different by Drip but go to the same address.

This module retrieves all of the email addresses of subscribers on your Drip email account and
groups together addresses that resolve to the same inbox: comparison is case-insensitive, `+` aliases
are stripped, and dots in the username are ignored for Gmail addresses (where they are insignificant).
A report is generated as an Excel spreadsheet — one row per duplicate group — and emailed to staff
for profile merging. This is designed to be run as a regular cron job. Drip doesn't support automated
profile merging, so a person will need to manually perform the merges based on the report.
