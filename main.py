#!/usr/local/bin/python3.10

from find_dupes import find_duplicates
from save_excel import save_excel
from datetime import datetime
from send_email import email_spreadsheet
from drip import retrieve_emails
import os

if __name__ == '__main__':
    email_list = retrieve_emails()
    results = find_duplicates(email_list)

    spreadsheet_name = f'files/duplicate_emails_{datetime.now().strftime("%-m_%-d_%y")}.xlsx'
    save_excel(results, spreadsheet_name)
    recips = os.environ.get('RECIPS').split(', ')
    for i in recips:
        email_spreadsheet(spreadsheet_name, i)
