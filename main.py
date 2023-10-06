#!/usr/bin/env python3.10

from find_dupes import check_equivalence
from separate_by_letter import separate_by_letter
from save_excel import save_excel
from datetime import datetime
from send_email import email_spreadsheet
from drip import retrieve_emails
from separate_by_letter import separate_by_letter
from multiprocess import multiprocess_checks
import os

if __name__ == '__main__':
    # Get email list
    email_list = retrieve_emails()

    # Separate emails by first letter
    emails_by_first_letter = separate_by_letter(email_list)

    # Check for duplicates
    results = multiprocess_checks(emails_by_first_letter, check_equivalence)

    # print(results)
    spreadsheet_name = f'files/duplicate_emails_{datetime.now().strftime("%-m_%-d_%y")}.xlsx'
    save_excel(results, spreadsheet_name)
    recips = os.environ.get('RECIPS').split(', ')
    for i in recips:
        email_spreadsheet(spreadsheet_name, i)
