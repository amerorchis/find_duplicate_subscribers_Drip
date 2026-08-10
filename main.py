"""Find duplicate Drip subscribers and email the report to the configured recipients."""

import os
import sys
from datetime import datetime

from drip import retrieve_emails
from find_dupes import find_duplicates
from save_excel import save_excel
from send_email import email_spreadsheet

REQUIRED_ENV_VARS = ['DRIP_TOKEN', 'DRIP_ACCOUNT', 'FROM_ALERT_EMAIL',
                     'FROM_ALERT_PWD', 'RECIPS']


def main():
    """Run the full pipeline: fetch, find duplicates, save spreadsheet, email it."""
    missing = [var for var in REQUIRED_ENV_VARS if not os.environ.get(var)]
    if missing:
        sys.exit(f'Missing required environment variables: {", ".join(missing)}')

    recipients = [r.strip() for r in os.environ['RECIPS'].split(',') if r.strip()]

    email_list = retrieve_emails()
    results = find_duplicates(email_list)
    print(f'Found {len(results)} duplicate group(s)')

    os.makedirs('files', exist_ok=True)
    spreadsheet_name = f'files/duplicate_emails_{datetime.now().strftime("%-m_%-d_%y")}.xlsx'
    save_excel(results, spreadsheet_name)

    if os.environ.get('DRY_RUN'):
        print(f'DRY_RUN set: skipping email send. '
              f'Would have sent {spreadsheet_name} to {", ".join(recipients)}')
    else:
        email_spreadsheet(spreadsheet_name, recipients)


if __name__ == '__main__':
    main()
