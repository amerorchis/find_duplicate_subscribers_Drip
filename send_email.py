import smtplib
from datetime import date
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import os

def email_spreadsheet(spreadsheet):
    from_address = os.environ.get('FROM_ALERT_EMAIL')
    from_password = os.environ.get('FROM_ALERT_PWD')
    to_email = os.environ.get('RECIPS')

    # instance of MIMEMultipart
    msg = MIMEMultipart()

    msg['From'] = from_address
    msg['To'] = to_email

    date_ = date.today()
    msg['Subject'] = f"Duplicate Drip Subscribers report for {date_.month}/{date_.day}"    
    body = "Here's the report on duplicate subscribers in Drip that correspond to the same email address."

    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    if spreadsheet:
        # open the file to be sent 
        attachment = open(spreadsheet, "rb")

        # instance of MIMEBase and named as p
        p = MIMEBase('application', 'octet-stream')

        # To change the payload into encoded form
        p.set_payload((attachment).read())

        # encode into base64
        encoders.encode_base64(p)
        p.add_header('Content-Disposition', "attachment; filename= %s" % spreadsheet)

        # attach the instance 'p' to instance 'msg'
        msg.attach(p)

    # creates SMTP session and start ttls
    s = smtplib.SMTP('smtp.gmail.com', 587)
    s.starttls()

    s.login(from_address, from_password) # Authentication

    text = msg.as_string() # Converts the Multipart msg into a string

    # send the mail and terminate
    s.sendmail(from_address, to_email, text)
    s.quit()

    print('email sent')
