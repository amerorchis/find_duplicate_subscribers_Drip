# find_duplicate_subscribers_Drip
Generate a report of emails that are recognized as different by Drip but go to same address.

This module retrieves all of the email addresses of subscribers on your Drip email account. 
It checks each one to make sure that it is not identical to any other email address when ignoring punctuation 
ignored by the email service (ie periods and "+" in gmail)leveraging multiprocessing for improved performance.
A report is generated as an excel spreadsheet that can be emailed to staff for profile merging.
This is designed to be run as a regular cron job. Drip doesn't support automated profile merging, so a person
will need to manually perform the merges based on the report.
