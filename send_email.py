"""Email the duplicate-subscriber spreadsheet to each recipient via Gmail SMTP."""

import logging
import os
import smtplib
from datetime import date
from email.message import EmailMessage

from log_utils import mask_email

XLSX_MIME = ('application', 'vnd.openxmlformats-officedocument.spreadsheetml.sheet')

logger = logging.getLogger(__name__)


def email_spreadsheet(spreadsheet, recipients):
    """Send the spreadsheet to each recipient as a separate email over one SMTP session."""
    from_address = os.environ.get('FROM_ALERT_EMAIL')
    from_password = os.environ.get('FROM_ALERT_PWD')

    attachment_data = None
    if spreadsheet:
        with open(spreadsheet, 'rb') as file:
            attachment_data = file.read()

    today = date.today()

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login(from_address, from_password)

        for to_email in recipients:
            msg = EmailMessage()
            msg['From'] = from_address
            msg['To'] = to_email
            msg['Subject'] = f'Duplicate Drip Subscribers report for {today.month}/{today.day}'
            msg.set_content("Here's the report on duplicate subscribers in Drip "
                            'that correspond to the same email address.')

            if attachment_data:
                maintype, subtype = XLSX_MIME
                msg.add_attachment(attachment_data, maintype=maintype, subtype=subtype,
                                   filename=os.path.basename(spreadsheet))

            smtp.send_message(msg)
            logger.info('Email sent to %s', mask_email(to_email))
